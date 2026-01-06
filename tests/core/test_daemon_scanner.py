# ClamUI Daemon Scanner Tests
"""Unit tests for the daemon scanner module."""

from unittest.mock import MagicMock, patch

import pytest

# Import directly - daemon_scanner uses GLib only for idle_add in async methods,
# and those methods are not tested here (unit tests mock the async behavior)
from src.core.daemon_scanner import DaemonScanner
from src.core.scanner import ScanStatus
from src.core.threat_classifier import categorize_threat, classify_threat_severity_str


@pytest.fixture
def daemon_scanner_class():
    """Get DaemonScanner class."""
    return DaemonScanner


@pytest.fixture
def scan_status_class():
    """Get ScanStatus enum."""
    return ScanStatus


@pytest.fixture
def daemon_scanner():
    """Create a DaemonScanner instance for testing."""
    return DaemonScanner()


class TestDaemonScannerCheckAvailable:
    """Tests for DaemonScanner.check_available method."""

    def test_check_available_when_daemon_running(self, daemon_scanner_class):
        """Test availability check when clamd is running."""
        scanner = daemon_scanner_class()

        with patch("src.core.daemon_scanner.check_clamdscan_installed") as mock_installed:
            mock_installed.return_value = (True, "ClamAV 1.0.0")
            with patch("src.core.daemon_scanner.check_clamd_connection") as mock_connection:
                mock_connection.return_value = (True, "PONG")

                available, msg = scanner.check_available()

        assert available is True
        assert "available" in msg.lower()

    def test_check_available_clamdscan_not_installed(self, daemon_scanner_class):
        """Test availability check when clamdscan is not installed."""
        scanner = daemon_scanner_class()

        with patch("src.core.daemon_scanner.check_clamdscan_installed") as mock_installed:
            mock_installed.return_value = (False, "clamdscan not found")

            available, msg = scanner.check_available()

        assert available is False
        assert "not found" in msg.lower() or "clamdscan" in msg.lower()

    def test_check_available_daemon_not_running(self, daemon_scanner_class):
        """Test availability check when clamd is not running."""
        scanner = daemon_scanner_class()

        with patch("src.core.daemon_scanner.check_clamdscan_installed") as mock_installed:
            mock_installed.return_value = (True, "ClamAV 1.0.0")
            with patch("src.core.daemon_scanner.check_clamd_connection") as mock_connection:
                mock_connection.return_value = (False, "Connection refused")

                available, msg = scanner.check_available()

        assert available is False
        assert "not accessible" in msg.lower() or "connection" in msg.lower()


class TestDaemonScannerBuildCommand:
    """Tests for DaemonScanner._build_command method."""

    def test_build_command_basic(self, tmp_path, daemon_scanner_class):
        """Test _build_command builds correct clamdscan command."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        scanner = daemon_scanner_class()

        with patch("src.core.daemon_scanner.which_host_command", return_value="/usr/bin/clamdscan"):
            with patch("src.core.daemon_scanner.wrap_host_command", side_effect=lambda x: x):
                cmd = scanner._build_command(str(test_file), recursive=True)

        assert cmd[0] == "/usr/bin/clamdscan"
        assert "--multiscan" in cmd
        assert "--fdpass" in cmd
        assert "-i" in cmd
        assert str(test_file) in cmd

    def test_build_command_fallback_to_clamdscan(self, tmp_path, daemon_scanner_class):
        """Test _build_command falls back to 'clamdscan' when path not found."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        scanner = daemon_scanner_class()

        with patch("src.core.daemon_scanner.which_host_command", return_value=None):
            with patch("src.core.daemon_scanner.wrap_host_command", side_effect=lambda x: x):
                cmd = scanner._build_command(str(test_file), recursive=True)

        assert cmd[0] == "clamdscan"

    def test_build_command_without_exclusions(self, tmp_path, daemon_scanner_class):
        """Test _build_command does NOT include --exclude (clamdscan doesn't support it)."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        mock_settings = MagicMock()
        mock_settings.get.return_value = [
            {"pattern": "*.log", "type": "file", "enabled": True},
            {"pattern": "node_modules", "type": "directory", "enabled": True},
        ]

        scanner = daemon_scanner_class(settings_manager=mock_settings)

        with patch("src.core.daemon_scanner.which_host_command", return_value="/usr/bin/clamdscan"):
            with patch("src.core.daemon_scanner.wrap_host_command", side_effect=lambda x: x):
                cmd = scanner._build_command(str(test_file), recursive=True)

        # clamdscan does NOT support --exclude options (they're silently ignored)
        # Exclusions are handled post-scan via _filter_excluded_threats()
        assert "--exclude" not in cmd
        assert "--exclude-dir" not in cmd


class TestDaemonScannerParseResults:
    """Tests for DaemonScanner._parse_results method."""

    def test_parse_results_clean_scan(self, daemon_scanner_class, scan_status_class):
        """Test parsing clean scan results."""
        scanner = daemon_scanner_class()

        # clamdscan output doesn't include file/directory counts,
        # so they are passed as parameters from pre-counting
        stdout = """
/home/user/test.txt: OK

----------- SCAN SUMMARY -----------
Infected files: 0
"""
        result = scanner._parse_results("/home/user", stdout, "", 0, file_count=1, dir_count=0)

        assert result.status == scan_status_class.CLEAN
        assert result.infected_count == 0
        assert result.scanned_files == 1

    def test_parse_results_infected_scan(self, daemon_scanner_class, scan_status_class):
        """Test parsing infected scan results."""
        scanner = daemon_scanner_class()

        # clamdscan output with -i flag only shows infected files
        stdout = """
/home/user/malware.exe: Win.Trojan.Agent FOUND

----------- SCAN SUMMARY -----------
Infected files: 1
"""
        result = scanner._parse_results("/home/user", stdout, "", 1, file_count=1, dir_count=0)

        assert result.status == scan_status_class.INFECTED
        assert result.infected_count == 1
        assert len(result.threat_details) == 1
        assert result.threat_details[0].threat_name == "Win.Trojan.Agent"
        assert result.threat_details[0].file_path == "/home/user/malware.exe"

    def test_parse_results_error(self, daemon_scanner_class, scan_status_class):
        """Test parsing error scan results."""
        scanner = daemon_scanner_class()

        result = scanner._parse_results("/home/user", "", "Connection refused", 2)

        assert result.status == scan_status_class.ERROR
        assert result.error_message is not None


class TestDaemonScannerThreatClassification:
    """Tests for threat classification functions."""

    def test_classify_threat_severity_critical(self):
        """Test classifying ransomware as critical."""
        severity = classify_threat_severity_str("Win.Ransomware.Locky")
        assert severity == "critical"

    def test_classify_threat_severity_high(self):
        """Test classifying trojan as high severity."""
        severity = classify_threat_severity_str("Win.Trojan.Agent")
        assert severity == "high"

    def test_classify_threat_severity_low(self):
        """Test classifying EICAR test as low severity."""
        severity = classify_threat_severity_str("Eicar-Test-Signature")
        assert severity == "low"

    def test_categorize_threat_trojan(self):
        """Test categorizing a trojan threat."""
        category = categorize_threat("Win.Trojan.Agent")
        assert category == "Trojan"

    def test_categorize_threat_ransomware(self):
        """Test categorizing a ransomware threat."""
        category = categorize_threat("Win.Ransomware.Locky")
        assert category == "Ransomware"


class TestDaemonScannerCancel:
    """Tests for DaemonScanner.cancel method."""

    def test_cancel_sets_flag(self, daemon_scanner_class):
        """Test that cancel sets the cancelled flag."""
        scanner = daemon_scanner_class()

        scanner.cancel()

        assert scanner._scan_cancelled is True

    def test_cancel_terminates_process(self, daemon_scanner_class):
        """Test that cancel terminates running process."""
        scanner = daemon_scanner_class()
        mock_process = MagicMock()
        scanner._current_process = mock_process

        scanner.cancel()

        mock_process.terminate.assert_called_once()


class TestDaemonScannerFilterExcludedThreats:
    """Tests for DaemonScanner._filter_excluded_threats method."""

    def test_filter_excludes_exact_path_match(self, daemon_scanner_class, scan_status_class):
        """Test that exact path matches are filtered out."""
        mock_settings = MagicMock()
        mock_settings.get.return_value = [
            {"pattern": "/home/user/eicar.txt", "type": "file", "enabled": True},
        ]
        scanner = daemon_scanner_class(settings_manager=mock_settings)

        # Create a mock ThreatDetail
        from src.core.scanner import ThreatDetail

        threat = ThreatDetail(
            file_path="/home/user/eicar.txt",
            threat_name="Eicar-Test-Signature",
            category="Test",
            severity="low",
        )

        # Create infected result
        from src.core.scanner import ScanResult

        result = ScanResult(
            status=scan_status_class.INFECTED,
            path="/home/user",
            stdout="",
            stderr="",
            exit_code=1,
            infected_files=["/home/user/eicar.txt"],
            scanned_files=1,
            scanned_dirs=0,
            infected_count=1,
            error_message=None,
            threat_details=[threat],
        )

        filtered = scanner._filter_excluded_threats(result)

        # Should be clean since threat was excluded
        assert filtered.status == scan_status_class.CLEAN
        assert filtered.infected_count == 0
        assert len(filtered.threat_details) == 0

    def test_filter_keeps_non_excluded_threats(self, daemon_scanner_class, scan_status_class):
        """Test that non-excluded threats are kept."""
        mock_settings = MagicMock()
        mock_settings.get.return_value = [
            {"pattern": "/some/other/path.txt", "type": "file", "enabled": True},
        ]
        scanner = daemon_scanner_class(settings_manager=mock_settings)

        from src.core.scanner import ScanResult, ThreatDetail

        threat = ThreatDetail(
            file_path="/home/user/virus.exe",
            threat_name="Win.Trojan.Test",
            category="Trojan",
            severity="high",
        )

        result = ScanResult(
            status=scan_status_class.INFECTED,
            path="/home/user",
            stdout="",
            stderr="",
            exit_code=1,
            infected_files=["/home/user/virus.exe"],
            scanned_files=1,
            scanned_dirs=0,
            infected_count=1,
            error_message=None,
            threat_details=[threat],
        )

        filtered = scanner._filter_excluded_threats(result)

        # Should still be infected
        assert filtered.status == scan_status_class.INFECTED
        assert filtered.infected_count == 1
        assert len(filtered.threat_details) == 1

    def test_filter_respects_disabled_exclusions(self, daemon_scanner_class, scan_status_class):
        """Test that disabled exclusions don't filter threats."""
        mock_settings = MagicMock()
        mock_settings.get.return_value = [
            {"pattern": "/home/user/eicar.txt", "type": "file", "enabled": False},
        ]
        scanner = daemon_scanner_class(settings_manager=mock_settings)

        from src.core.scanner import ScanResult, ThreatDetail

        threat = ThreatDetail(
            file_path="/home/user/eicar.txt",
            threat_name="Eicar-Test-Signature",
            category="Test",
            severity="low",
        )

        result = ScanResult(
            status=scan_status_class.INFECTED,
            path="/home/user",
            stdout="",
            stderr="",
            exit_code=1,
            infected_files=["/home/user/eicar.txt"],
            scanned_files=1,
            scanned_dirs=0,
            infected_count=1,
            error_message=None,
            threat_details=[threat],
        )

        filtered = scanner._filter_excluded_threats(result)

        # Should still be infected since exclusion is disabled
        assert filtered.status == scan_status_class.INFECTED
        assert filtered.infected_count == 1


class TestDaemonScannerCountTargets:
    """Tests for DaemonScanner count_targets parameter."""

    def test_scan_sync_with_count_targets_true_counts_files(
        self, tmp_path, daemon_scanner_class, scan_status_class
    ):
        """Test that count_targets=True (default) counts files and directories."""
        # Create test directory structure
        test_dir = tmp_path / "scan_test"
        test_dir.mkdir()
        (test_dir / "file1.txt").write_text("content1")
        (test_dir / "file2.txt").write_text("content2")
        subdir = test_dir / "subdir"
        subdir.mkdir()
        (subdir / "file3.txt").write_text("content3")

        scanner = daemon_scanner_class()

        with (
            patch("src.core.daemon_scanner.check_clamdscan_installed") as mock_installed,
            patch("src.core.daemon_scanner.check_clamd_connection") as mock_connection,
            patch("subprocess.Popen") as mock_popen,
        ):
            mock_installed.return_value = (True, "ClamAV 1.0.0")
            mock_connection.return_value = (True, "PONG")

            mock_process = MagicMock()
            mock_process.communicate.return_value = ("", "")
            mock_process.returncode = 0
            mock_popen.return_value = mock_process

            result = scanner.scan_sync(str(test_dir), count_targets=True)

        assert result.status == scan_status_class.CLEAN
        # Should have counted files (3 files)
        assert result.scanned_files == 3
        # Should have counted directories (root + subdir = 2)
        assert result.scanned_dirs == 2

    def test_scan_sync_with_count_targets_false_skips_counting(
        self, tmp_path, daemon_scanner_class, scan_status_class
    ):
        """Test that count_targets=False skips file/directory counting."""
        # Create test directory structure
        test_dir = tmp_path / "scan_test"
        test_dir.mkdir()
        (test_dir / "file1.txt").write_text("content1")
        (test_dir / "file2.txt").write_text("content2")
        subdir = test_dir / "subdir"
        subdir.mkdir()
        (subdir / "file3.txt").write_text("content3")

        scanner = daemon_scanner_class()

        with (
            patch("src.core.daemon_scanner.check_clamdscan_installed") as mock_installed,
            patch("src.core.daemon_scanner.check_clamd_connection") as mock_connection,
            patch("subprocess.Popen") as mock_popen,
        ):
            mock_installed.return_value = (True, "ClamAV 1.0.0")
            mock_connection.return_value = (True, "PONG")

            mock_process = MagicMock()
            mock_process.communicate.return_value = ("", "")
            mock_process.returncode = 0
            mock_popen.return_value = mock_process

            result = scanner.scan_sync(str(test_dir), count_targets=False)

        assert result.status == scan_status_class.CLEAN
        # Counts should be 0 when count_targets=False
        assert result.scanned_files == 0
        assert result.scanned_dirs == 0

    def test_scan_sync_count_targets_false_still_detects_infections(
        self, tmp_path, daemon_scanner_class, scan_status_class
    ):
        """Test that count_targets=False still correctly reports infections."""
        test_dir = tmp_path / "scan_test"
        test_dir.mkdir()
        (test_dir / "malware.exe").write_text("fake malware")

        scanner = daemon_scanner_class()

        with (
            patch("src.core.daemon_scanner.check_clamdscan_installed") as mock_installed,
            patch("src.core.daemon_scanner.check_clamd_connection") as mock_connection,
            patch("subprocess.Popen") as mock_popen,
        ):
            mock_installed.return_value = (True, "ClamAV 1.0.0")
            mock_connection.return_value = (True, "PONG")

            mock_process = MagicMock()
            infected_output = f"{test_dir}/malware.exe: Win.Trojan.Test FOUND\n"
            mock_process.communicate.return_value = (infected_output, "")
            mock_process.returncode = 1
            mock_popen.return_value = mock_process

            result = scanner.scan_sync(str(test_dir), count_targets=False)

        # Should still detect infection
        assert result.status == scan_status_class.INFECTED
        assert result.infected_count == 1
        assert len(result.threat_details) == 1
        assert result.threat_details[0].threat_name == "Win.Trojan.Test"
        # But counts should still be 0
        assert result.scanned_files == 0
        assert result.scanned_dirs == 0

    def test_scan_sync_default_count_targets_is_true(
        self, tmp_path, daemon_scanner_class, scan_status_class
    ):
        """Test that count_targets defaults to True for backwards compatibility."""
        test_dir = tmp_path / "scan_test"
        test_dir.mkdir()
        (test_dir / "file.txt").write_text("content")

        scanner = daemon_scanner_class()

        with (
            patch("src.core.daemon_scanner.check_clamdscan_installed") as mock_installed,
            patch("src.core.daemon_scanner.check_clamd_connection") as mock_connection,
            patch("subprocess.Popen") as mock_popen,
            patch.object(scanner, "_count_scan_targets") as mock_count,
        ):
            mock_installed.return_value = (True, "ClamAV 1.0.0")
            mock_connection.return_value = (True, "PONG")
            mock_count.return_value = (1, 1)

            mock_process = MagicMock()
            mock_process.communicate.return_value = ("", "")
            mock_process.returncode = 0
            mock_popen.return_value = mock_process

            # Call without count_targets parameter (should default to True)
            scanner.scan_sync(str(test_dir))

        # _count_scan_targets should have been called
        mock_count.assert_called_once()

    def test_scan_async_passes_count_targets_to_sync(self, tmp_path, daemon_scanner_class):
        """Test that scan_async passes count_targets to scan_sync."""
        test_dir = tmp_path / "scan_test"
        test_dir.mkdir()

        scanner = daemon_scanner_class()
        callback = MagicMock()

        with (
            patch.object(scanner, "scan_sync") as mock_sync,
            patch("src.core.daemon_scanner.GLib.idle_add"),
        ):
            from src.core.scanner import ScanResult, ScanStatus

            mock_sync.return_value = ScanResult(
                status=ScanStatus.CLEAN,
                path=str(test_dir),
                stdout="",
                stderr="",
                exit_code=0,
                infected_files=[],
                scanned_files=0,
                scanned_dirs=0,
                infected_count=0,
                error_message=None,
                threat_details=[],
            )

            # Call async with count_targets=False
            scanner.scan_async(str(test_dir), callback, count_targets=False)

            # Wait for thread to execute
            import time

            time.sleep(0.1)

        # Verify scan_sync was called with count_targets=False
        mock_sync.assert_called_once()
        call_args = mock_sync.call_args
        assert call_args[0][0] == str(test_dir)  # path
        assert call_args[0][3] is False  # count_targets (4th positional arg)
