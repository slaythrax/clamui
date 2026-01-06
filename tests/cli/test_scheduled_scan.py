# ClamUI Scheduled Scan CLI Tests
"""Unit tests for the scheduled scan CLI module functions."""

import os
import subprocess
from unittest.mock import MagicMock, patch


class TestParseArguments:
    """Tests for the parse_arguments function."""

    def test_parse_arguments_default_values(self):
        """Test parse_arguments returns default values when no args provided."""
        from src.cli.scheduled_scan import parse_arguments

        with patch("sys.argv", ["clamui-scheduled-scan"]):
            args = parse_arguments()

        assert args.skip_on_battery is None
        assert args.auto_quarantine is None
        assert args.targets is None
        assert args.dry_run is False
        assert args.verbose is False

    def test_parse_arguments_skip_on_battery(self):
        """Test parse_arguments with --skip-on-battery flag."""
        from src.cli.scheduled_scan import parse_arguments

        with patch("sys.argv", ["clamui-scheduled-scan", "--skip-on-battery"]):
            args = parse_arguments()

        assert args.skip_on_battery is True

    def test_parse_arguments_auto_quarantine(self):
        """Test parse_arguments with --auto-quarantine flag."""
        from src.cli.scheduled_scan import parse_arguments

        with patch("sys.argv", ["clamui-scheduled-scan", "--auto-quarantine"]):
            args = parse_arguments()

        assert args.auto_quarantine is True

    def test_parse_arguments_single_target(self):
        """Test parse_arguments with single --target."""
        from src.cli.scheduled_scan import parse_arguments

        with patch("sys.argv", ["clamui-scheduled-scan", "--target", "/home/user"]):
            args = parse_arguments()

        assert args.targets == ["/home/user"]

    def test_parse_arguments_multiple_targets(self):
        """Test parse_arguments with multiple --target flags."""
        from src.cli.scheduled_scan import parse_arguments

        with patch(
            "sys.argv",
            ["clamui-scheduled-scan", "--target", "/home/user", "--target", "/tmp"],
        ):
            args = parse_arguments()

        assert args.targets == ["/home/user", "/tmp"]

    def test_parse_arguments_dry_run(self):
        """Test parse_arguments with --dry-run flag."""
        from src.cli.scheduled_scan import parse_arguments

        with patch("sys.argv", ["clamui-scheduled-scan", "--dry-run"]):
            args = parse_arguments()

        assert args.dry_run is True

    def test_parse_arguments_verbose(self):
        """Test parse_arguments with --verbose flag."""
        from src.cli.scheduled_scan import parse_arguments

        with patch("sys.argv", ["clamui-scheduled-scan", "--verbose"]):
            args = parse_arguments()

        assert args.verbose is True

    def test_parse_arguments_verbose_short_form(self):
        """Test parse_arguments with -v flag."""
        from src.cli.scheduled_scan import parse_arguments

        with patch("sys.argv", ["clamui-scheduled-scan", "-v"]):
            args = parse_arguments()

        assert args.verbose is True

    def test_parse_arguments_all_options(self):
        """Test parse_arguments with all options combined."""
        from src.cli.scheduled_scan import parse_arguments

        with patch(
            "sys.argv",
            [
                "clamui-scheduled-scan",
                "--skip-on-battery",
                "--auto-quarantine",
                "--target",
                "/home",
                "--target",
                "/tmp",
                "--dry-run",
                "--verbose",
            ],
        ):
            args = parse_arguments()

        assert args.skip_on_battery is True
        assert args.auto_quarantine is True
        assert args.targets == ["/home", "/tmp"]
        assert args.dry_run is True
        assert args.verbose is True


class TestLogMessage:
    """Tests for the log_message function."""

    def test_log_message_basic(self, capsys):
        """Test log_message outputs to stderr."""
        from src.cli.scheduled_scan import log_message

        log_message("Test message", verbose=False)

        captured = capsys.readouterr()
        assert "Test message" in captured.err
        assert captured.out == ""

    def test_log_message_verbose_only_not_shown(self, capsys):
        """Test verbose-only message not shown when verbose=False."""
        from src.cli.scheduled_scan import log_message

        log_message("Verbose message", verbose=False, is_verbose=True)

        captured = capsys.readouterr()
        assert "Verbose message" not in captured.err

    def test_log_message_verbose_only_shown(self, capsys):
        """Test verbose-only message shown when verbose=True."""
        from src.cli.scheduled_scan import log_message

        log_message("Verbose message", verbose=True, is_verbose=True)

        captured = capsys.readouterr()
        assert "Verbose message" in captured.err

    def test_log_message_timestamp_format(self, capsys):
        """Test log_message includes timestamp."""
        from src.cli.scheduled_scan import log_message

        log_message("Test", verbose=False)

        captured = capsys.readouterr()
        # Check for timestamp format: [YYYY-MM-DD HH:MM:SS]
        assert "[20" in captured.err
        assert "]" in captured.err


class TestSendNotification:
    """Tests for the send_notification function."""

    def test_send_notification_success(self):
        """Test send_notification returns True on success."""
        from src.cli.scheduled_scan import send_notification

        mock_result = MagicMock()
        mock_result.returncode = 0

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            result = send_notification("Title", "Body")

        assert result is True
        mock_run.assert_called_once()
        # Check that notify-send was called with the right args
        call_args = mock_run.call_args[0][0]
        assert "notify-send" in call_args
        assert "Title" in call_args
        assert "Body" in call_args

    def test_send_notification_with_urgency(self):
        """Test send_notification with different urgency levels."""
        from src.cli.scheduled_scan import send_notification

        mock_result = MagicMock()
        mock_result.returncode = 0

        for urgency in ["low", "normal", "critical"]:
            with patch("subprocess.run", return_value=mock_result) as mock_run:
                result = send_notification("Title", "Body", urgency=urgency)

            assert result is True
            call_args = mock_run.call_args[0][0]
            assert "--urgency" in call_args
            assert urgency in call_args

    def test_send_notification_file_not_found(self):
        """Test send_notification returns False when notify-send not found."""
        from src.cli.scheduled_scan import send_notification

        with patch("subprocess.run", side_effect=FileNotFoundError):
            result = send_notification("Title", "Body")

        assert result is False

    def test_send_notification_timeout(self):
        """Test send_notification returns False on timeout."""
        from src.cli.scheduled_scan import send_notification

        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("cmd", 5)):
            result = send_notification("Title", "Body")

        assert result is False

    def test_send_notification_oserror(self):
        """Test send_notification returns False on OSError."""
        from src.cli.scheduled_scan import send_notification

        with patch("subprocess.run", side_effect=OSError("Some error")):
            result = send_notification("Title", "Body")

        assert result is False

    def test_send_notification_failure_returncode(self):
        """Test send_notification returns False on non-zero return code."""
        from src.cli.scheduled_scan import send_notification

        mock_result = MagicMock()
        mock_result.returncode = 1

        with patch("subprocess.run", return_value=mock_result):
            result = send_notification("Title", "Body")

        assert result is False


class TestRunScheduledScan:
    """Tests for the run_scheduled_scan function."""

    def test_run_scheduled_scan_dry_run(self, tmp_path, capsys):
        """Test run_scheduled_scan in dry run mode."""
        from src.cli.scheduled_scan import run_scheduled_scan

        target = tmp_path / "test_dir"
        target.mkdir()

        result = run_scheduled_scan(
            targets=[str(target)],
            skip_on_battery=True,
            auto_quarantine=True,
            dry_run=True,
            verbose=True,
        )

        assert result == 0
        captured = capsys.readouterr()
        assert "Dry run mode" in captured.err

    def test_run_scheduled_scan_no_targets(self, capsys):
        """Test run_scheduled_scan with no targets returns error."""
        from src.cli.scheduled_scan import run_scheduled_scan

        result = run_scheduled_scan(
            targets=[],
            skip_on_battery=False,
            auto_quarantine=False,
            dry_run=False,
            verbose=True,
        )

        assert result == 2
        captured = capsys.readouterr()
        assert "No scan targets" in captured.err

    def test_run_scheduled_scan_invalid_targets(self, capsys):
        """Test run_scheduled_scan with all invalid targets returns error."""
        from src.cli.scheduled_scan import run_scheduled_scan

        result = run_scheduled_scan(
            targets=["/nonexistent/path/1", "/nonexistent/path/2"],
            skip_on_battery=False,
            auto_quarantine=False,
            dry_run=False,
            verbose=True,
        )

        assert result == 2
        captured = capsys.readouterr()
        assert "No valid scan targets" in captured.err

    def test_run_scheduled_scan_skip_on_battery(self, tmp_path, capsys):
        """Test run_scheduled_scan skips scan when on battery."""
        from src.cli.scheduled_scan import run_scheduled_scan

        target = tmp_path / "test_dir"
        target.mkdir()

        # Mock BatteryManager to report on battery
        with patch("src.cli.scheduled_scan.BatteryManager") as mock_bm_class:
            mock_bm = MagicMock()
            mock_bm.should_skip_scan.return_value = True
            mock_bm.get_status.return_value = MagicMock(percent=50.0)
            mock_bm_class.return_value = mock_bm

            # Mock LogManager
            with patch("src.cli.scheduled_scan.LogManager") as mock_lm_class:
                mock_lm = MagicMock()
                mock_lm_class.return_value = mock_lm

                result = run_scheduled_scan(
                    targets=[str(target)],
                    skip_on_battery=True,
                    auto_quarantine=False,
                    dry_run=False,
                    verbose=True,
                )

        assert result == 0
        captured = capsys.readouterr()
        assert "Skipping scan" in captured.err
        assert "battery" in captured.err.lower()

    def test_run_scheduled_scan_clamav_not_available(self, tmp_path, capsys):
        """Test run_scheduled_scan when ClamAV not available."""
        from src.cli.scheduled_scan import run_scheduled_scan

        target = tmp_path / "test_dir"
        target.mkdir()

        # Mock Scanner to report ClamAV not available
        with patch("src.cli.scheduled_scan.Scanner") as mock_scanner_class:
            mock_scanner = MagicMock()
            mock_scanner.check_available.return_value = (False, "ClamAV not found")
            mock_scanner_class.return_value = mock_scanner

            # Mock LogManager
            with patch("src.cli.scheduled_scan.LogManager") as mock_lm_class:
                mock_lm = MagicMock()
                mock_lm_class.return_value = mock_lm

                # Mock send_notification
                with patch("src.cli.scheduled_scan.send_notification"):
                    result = run_scheduled_scan(
                        targets=[str(target)],
                        skip_on_battery=False,
                        auto_quarantine=False,
                        dry_run=False,
                        verbose=True,
                    )

        assert result == 2
        captured = capsys.readouterr()
        assert "ClamAV not available" in captured.err


class TestMain:
    """Tests for the main function."""

    def test_main_uses_settings_defaults(self):
        """Test main uses settings when CLI args not provided."""
        from src.cli.scheduled_scan import main

        mock_settings = MagicMock()
        mock_settings.get.side_effect = lambda key, default: {
            "schedule_skip_on_battery": True,
            "schedule_auto_quarantine": False,
            "schedule_targets": ["/home/test"],
        }.get(key, default)

        with patch("sys.argv", ["clamui-scheduled-scan", "--dry-run"]):
            with patch("src.cli.scheduled_scan.SettingsManager", return_value=mock_settings):
                with patch("src.cli.scheduled_scan.run_scheduled_scan") as mock_run:
                    mock_run.return_value = 0
                    result = main()

        assert result == 0
        mock_run.assert_called_once()
        call_kwargs = mock_run.call_args[1]
        assert call_kwargs["skip_on_battery"] is True
        assert call_kwargs["auto_quarantine"] is False
        assert call_kwargs["targets"] == ["/home/test"]

    def test_main_cli_overrides_settings(self):
        """Test main CLI args override settings."""
        from src.cli.scheduled_scan import main

        mock_settings = MagicMock()
        mock_settings.get.side_effect = lambda key, default: {
            "schedule_skip_on_battery": True,
            "schedule_auto_quarantine": False,
            "schedule_targets": ["/home/test"],
        }.get(key, default)

        with patch(
            "sys.argv",
            [
                "clamui-scheduled-scan",
                "--auto-quarantine",
                "--target",
                "/custom/path",
                "--dry-run",
            ],
        ):
            with patch("src.cli.scheduled_scan.SettingsManager", return_value=mock_settings):
                with patch("src.cli.scheduled_scan.run_scheduled_scan") as mock_run:
                    mock_run.return_value = 0
                    result = main()

        assert result == 0
        call_kwargs = mock_run.call_args[1]
        assert call_kwargs["auto_quarantine"] is True
        assert call_kwargs["targets"] == ["/custom/path"]

    def test_main_default_home_directory(self):
        """Test main defaults to home directory when no targets configured."""
        from src.cli.scheduled_scan import main

        mock_settings = MagicMock()
        mock_settings.get.side_effect = lambda key, default: {
            "schedule_skip_on_battery": False,
            "schedule_auto_quarantine": False,
            "schedule_targets": [],
        }.get(key, default)

        home_dir = os.path.expanduser("~")

        with patch("sys.argv", ["clamui-scheduled-scan", "--dry-run"]):
            with patch("src.cli.scheduled_scan.SettingsManager", return_value=mock_settings):
                with patch("src.cli.scheduled_scan.run_scheduled_scan") as mock_run:
                    mock_run.return_value = 0
                    result = main()

        assert result == 0
        call_kwargs = mock_run.call_args[1]
        assert call_kwargs["targets"] == [home_dir]
