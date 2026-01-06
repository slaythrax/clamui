# ClamUI ClamAV Config Tests
"""Unit tests for the ClamAV configuration module."""

import contextlib
import tempfile
from pathlib import Path

import pytest

from src.core.clamav_config import (
    ClamAVConfig,
    ClamAVConfigValue,
    parse_config,
)


class TestClamAVConfigValue:
    """Tests for the ClamAVConfigValue dataclass."""

    def test_create_default_values(self):
        """Test ClamAVConfigValue with default values."""
        config_value = ClamAVConfigValue(value="test")

        assert config_value.value == "test"
        assert config_value.comment is None
        assert config_value.line_number == 0

    def test_create_with_all_fields(self):
        """Test ClamAVConfigValue with all fields specified."""
        config_value = ClamAVConfigValue(
            value="/var/lib/clamav", comment="Database directory", line_number=5
        )

        assert config_value.value == "/var/lib/clamav"
        assert config_value.comment == "Database directory"
        assert config_value.line_number == 5


class TestClamAVConfig:
    """Tests for the ClamAVConfig dataclass."""

    def test_create_empty_config(self):
        """Test creating an empty ClamAVConfig."""
        config = ClamAVConfig(file_path=Path("/etc/clamav/freshclam.conf"))

        assert config.file_path == Path("/etc/clamav/freshclam.conf")
        assert config.values == {}
        assert config.raw_lines == []

    def test_get_value_existing(self):
        """Test get_value for existing key."""
        config = ClamAVConfig(file_path=Path("/test"))
        config.values["DatabaseDirectory"] = [ClamAVConfigValue(value="/var/lib/clamav")]

        assert config.get_value("DatabaseDirectory") == "/var/lib/clamav"

    def test_get_value_missing(self):
        """Test get_value for missing key."""
        config = ClamAVConfig(file_path=Path("/test"))

        assert config.get_value("NonExistent") is None

    def test_get_values_multiple(self):
        """Test get_values for multi-value option."""
        config = ClamAVConfig(file_path=Path("/test"))
        config.values["DatabaseMirror"] = [
            ClamAVConfigValue(value="database.clamav.net"),
            ClamAVConfigValue(value="db.local.clamav.net"),
        ]

        values = config.get_values("DatabaseMirror")
        assert len(values) == 2
        assert "database.clamav.net" in values
        assert "db.local.clamav.net" in values

    def test_set_value(self):
        """Test set_value replaces existing values."""
        config = ClamAVConfig(file_path=Path("/test"))
        config.values["LogVerbose"] = [ClamAVConfigValue(value="no")]

        config.set_value("LogVerbose", "yes")

        assert config.get_value("LogVerbose") == "yes"
        assert len(config.values["LogVerbose"]) == 1

    def test_add_value(self):
        """Test add_value appends to existing values."""
        config = ClamAVConfig(file_path=Path("/test"))
        config.add_value("DatabaseMirror", "mirror1.clamav.net")
        config.add_value("DatabaseMirror", "mirror2.clamav.net")

        values = config.get_values("DatabaseMirror")
        assert len(values) == 2

    def test_has_key_true(self):
        """Test has_key returns True for existing key."""
        config = ClamAVConfig(file_path=Path("/test"))
        config.set_value("LogVerbose", "yes")

        assert config.has_key("LogVerbose") is True

    def test_has_key_false(self):
        """Test has_key returns False for missing key."""
        config = ClamAVConfig(file_path=Path("/test"))

        assert config.has_key("NonExistent") is False

    def test_get_bool_yes(self):
        """Test get_bool returns True for 'yes'."""
        config = ClamAVConfig(file_path=Path("/test"))
        config.set_value("LogVerbose", "yes")

        assert config.get_bool("LogVerbose") is True

    def test_get_bool_no(self):
        """Test get_bool returns False for 'no'."""
        config = ClamAVConfig(file_path=Path("/test"))
        config.set_value("LogVerbose", "no")

        assert config.get_bool("LogVerbose") is False

    def test_get_bool_missing(self):
        """Test get_bool returns None for missing key."""
        config = ClamAVConfig(file_path=Path("/test"))

        assert config.get_bool("LogVerbose") is None

    def test_get_int_valid(self):
        """Test get_int returns integer for valid value."""
        config = ClamAVConfig(file_path=Path("/test"))
        config.set_value("Checks", "24")

        assert config.get_int("Checks") == 24

    def test_get_int_invalid(self):
        """Test get_int returns None for non-integer value."""
        config = ClamAVConfig(file_path=Path("/test"))
        config.set_value("Checks", "invalid")

        assert config.get_int("Checks") is None


class TestParseConfig:
    """Tests for the parse_config function."""

    @pytest.fixture
    def temp_config_file(self):
        """Create a temporary config file for testing."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".conf", delete=False, encoding="utf-8"
        ) as f:
            f.write("# ClamAV configuration\n")
            f.write("DatabaseDirectory /var/lib/clamav\n")
            f.write("LogVerbose yes\n")
            f.write("\n")
            f.write("Checks 24\n")
            temp_path = f.name
        yield temp_path
        with contextlib.suppress(OSError, PermissionError):
            Path(temp_path).unlink(missing_ok=True)

    def test_parse_valid_config(self, temp_config_file):
        """Test parsing a valid config file."""
        config, error = parse_config(temp_config_file)

        assert error is None
        assert config is not None
        assert config.get_value("DatabaseDirectory") == "/var/lib/clamav"
        assert config.get_value("LogVerbose") == "yes"
        assert config.get_value("Checks") == "24"

    def test_parse_empty_path(self):
        """Test parse_config with empty path."""
        config, error = parse_config("")

        assert config is None
        assert "no configuration file path" in error.lower()

    def test_parse_nonexistent_file(self):
        """Test parse_config with non-existent file."""
        config, error = parse_config("/nonexistent/config.conf")

        assert config is None
        assert "not found" in error.lower()

    def test_parse_directory_fails(self, tmp_path):
        """Test parse_config fails for directory path."""
        config, error = parse_config(str(tmp_path))

        assert config is None
        assert "not a file" in error.lower()

    def test_parse_preserves_raw_lines(self, temp_config_file):
        """Test that parse_config preserves raw lines."""
        config, error = parse_config(temp_config_file)

        assert error is None
        assert len(config.raw_lines) > 0

    def test_parse_config_with_inline_comments(self, tmp_path):
        """Test parsing config file with inline comments."""
        config_file = tmp_path / "test.conf"
        config_file.write_text("LogVerbose yes # Enable verbose logging\n")

        config, error = parse_config(str(config_file))

        assert error is None
        assert config.get_value("LogVerbose") == "yes"

    def test_parse_config_with_multi_value_options(self, tmp_path):
        """Test parsing config file with multiple values for same key."""
        config_file = tmp_path / "test.conf"
        config_file.write_text(
            "DatabaseMirror mirror1.clamav.net\nDatabaseMirror mirror2.clamav.net\n"
        )

        config, error = parse_config(str(config_file))

        assert error is None
        values = config.get_values("DatabaseMirror")
        assert len(values) == 2

    def test_parse_config_permission_denied(self, tmp_path):
        """Test parse_config handles permission denied."""

        config_file = tmp_path / "unreadable.conf"
        config_file.write_text("LogVerbose yes\n")
        original_mode = config_file.stat().st_mode
        config_file.chmod(0o000)

        try:
            config, error = parse_config(str(config_file))
            assert config is None
            assert "permission" in error.lower()
        finally:
            config_file.chmod(original_mode)

    def test_parse_config_invalid_path(self):
        """Test parse_config with invalid path format."""
        from unittest.mock import patch

        with patch.object(Path, "resolve", side_effect=OSError("Invalid path")):
            config, error = parse_config("some/path")
            assert config is None
            assert "invalid" in error.lower()


class TestValidateOption:
    """Tests for the validate_option function."""

    def test_validate_unknown_option(self):
        """Test validate_option allows unknown options."""
        from src.core.clamav_config import validate_option

        is_valid, error = validate_option("UnknownOption", "some_value")
        assert is_valid is True
        assert error is None

    def test_validate_boolean_yes(self):
        """Test validate_option accepts 'yes' for boolean."""
        from src.core.clamav_config import validate_option

        is_valid, error = validate_option("LogVerbose", "yes")
        assert is_valid is True
        assert error is None

    def test_validate_boolean_no(self):
        """Test validate_option accepts 'no' for boolean."""
        from src.core.clamav_config import validate_option

        is_valid, error = validate_option("LogVerbose", "no")
        assert is_valid is True
        assert error is None

    def test_validate_boolean_invalid(self):
        """Test validate_option rejects invalid boolean."""
        from src.core.clamav_config import validate_option

        is_valid, error = validate_option("LogVerbose", "maybe")
        assert is_valid is False
        assert "invalid boolean" in error.lower()

    def test_validate_path_valid(self):
        """Test validate_option accepts valid path."""
        from src.core.clamav_config import validate_option

        is_valid, error = validate_option("DatabaseDirectory", "/var/lib/clamav")
        assert is_valid is True
        assert error is None

    def test_validate_path_empty(self):
        """Test validate_option rejects empty path."""
        from src.core.clamav_config import validate_option

        is_valid, error = validate_option("DatabaseDirectory", "")
        assert is_valid is False
        assert "empty" in error.lower()

    def test_validate_integer_valid(self):
        """Test validate_option accepts valid integer."""
        from src.core.clamav_config import validate_option

        is_valid, error = validate_option("Checks", "24")
        assert is_valid is True
        assert error is None

    def test_validate_integer_invalid(self):
        """Test validate_option rejects non-integer."""
        from src.core.clamav_config import validate_option

        is_valid, error = validate_option("Checks", "not_a_number")
        assert is_valid is False
        assert "not a valid integer" in error.lower()

    def test_validate_integer_below_min(self):
        """Test validate_option rejects integer below minimum."""
        from src.core.clamav_config import validate_option

        is_valid, error = validate_option("Checks", "-1")
        assert is_valid is False
        assert "below minimum" in error.lower()

    def test_validate_integer_above_max(self):
        """Test validate_option rejects integer above maximum."""
        from src.core.clamav_config import validate_option

        is_valid, error = validate_option("Checks", "100")
        assert is_valid is False
        assert "exceeds maximum" in error.lower()

    def test_validate_size_valid(self):
        """Test validate_option accepts valid size."""
        from src.core.clamav_config import validate_option

        is_valid, error = validate_option("MaxFileSize", "100M")
        assert is_valid is True
        assert error is None

    def test_validate_size_empty(self):
        """Test validate_option rejects empty size."""
        from src.core.clamav_config import validate_option

        is_valid, error = validate_option("MaxFileSize", "")
        assert is_valid is False
        assert "empty" in error.lower()

    def test_validate_size_invalid(self):
        """Test validate_option rejects size not starting with digit."""
        from src.core.clamav_config import validate_option

        is_valid, error = validate_option("MaxFileSize", "M100")
        assert is_valid is False
        assert "must start with a number" in error.lower()

    def test_validate_string_valid(self):
        """Test validate_option accepts valid string."""
        from src.core.clamav_config import validate_option

        is_valid, error = validate_option("DatabaseMirror", "database.clamav.net")
        assert is_valid is True
        assert error is None

    def test_validate_string_empty(self):
        """Test validate_option rejects empty string."""
        from src.core.clamav_config import validate_option

        is_valid, error = validate_option("DatabaseMirror", "")
        assert is_valid is False
        assert "empty" in error.lower()


class TestWriteConfig:
    """Tests for the write_config function."""

    def test_write_config_success(self, tmp_path):
        """Test write_config writes successfully."""
        from src.core.clamav_config import write_config

        config_file = tmp_path / "test.conf"
        config_file.write_text("LogVerbose yes\n")

        config = ClamAVConfig(file_path=config_file)
        config.set_value("LogVerbose", "no", line_number=1)
        config.raw_lines = ["LogVerbose yes\n"]

        success, error = write_config(config)

        assert success is True
        assert error is None
        assert config_file.read_text() == "LogVerbose no\n"

    def test_write_config_no_path(self):
        """Test write_config fails with no path."""
        from src.core.clamav_config import write_config

        config = ClamAVConfig(file_path=None)

        success, error = write_config(config)

        assert success is False
        assert "no file path" in error.lower()

    def test_write_config_permission_denied(self, tmp_path):
        """Test write_config handles permission denied."""
        import stat

        from src.core.clamav_config import write_config

        config_file = tmp_path / "readonly.conf"
        config_file.write_text("LogVerbose yes\n")
        original_mode = config_file.stat().st_mode
        config_file.chmod(stat.S_IRUSR)

        config = ClamAVConfig(file_path=config_file)
        config.set_value("LogVerbose", "no")

        try:
            success, error = write_config(config)
            assert success is False
            assert "permission" in error.lower()
        finally:
            config_file.chmod(original_mode)


class TestValidateConfigFile:
    """Tests for the validate_config_file function."""

    def test_validate_config_file_success(self, tmp_path):
        """Test validate_config_file with valid config."""
        from src.core.clamav_config import validate_config_file

        config_file = tmp_path / "test.conf"
        config_file.write_text("LogVerbose yes\nChecks 24\n")

        is_valid, errors = validate_config_file(str(config_file))

        assert is_valid is True
        assert errors == []

    def test_validate_config_file_invalid_option(self, tmp_path):
        """Test validate_config_file with invalid option."""
        from src.core.clamav_config import validate_config_file

        config_file = tmp_path / "test.conf"
        config_file.write_text("LogVerbose maybe\n")

        is_valid, errors = validate_config_file(str(config_file))

        assert is_valid is False
        assert len(errors) > 0

    def test_validate_config_file_nonexistent(self):
        """Test validate_config_file with nonexistent file."""
        from src.core.clamav_config import validate_config_file

        is_valid, errors = validate_config_file("/nonexistent/path.conf")

        assert is_valid is False
        assert len(errors) > 0


class TestGetConfigSummary:
    """Tests for the get_config_summary function."""

    def test_get_config_summary_empty(self):
        """Test get_config_summary with empty config."""
        from src.core.clamav_config import get_config_summary

        config = ClamAVConfig(file_path=Path("/test"))

        summary = get_config_summary(config)

        assert "no configuration options" in summary.lower()

    def test_get_config_summary_with_values(self):
        """Test get_config_summary with values."""
        from src.core.clamav_config import get_config_summary

        config = ClamAVConfig(file_path=Path("/test/config.conf"))
        config.set_value("LogVerbose", "yes")
        config.set_value("Checks", "24")

        summary = get_config_summary(config)

        assert "/test/config.conf" in summary
        assert "LogVerbose" in summary
        assert "Checks" in summary


class TestValidateConfig:
    """Tests for the validate_config function."""

    def test_validate_config_valid(self):
        """Test validate_config with valid config."""
        from src.core.clamav_config import validate_config

        config = ClamAVConfig(file_path=Path("/test"))
        config.set_value("LogVerbose", "yes")
        config.set_value("Checks", "24")

        is_valid, errors = validate_config(config)

        assert is_valid is True
        assert errors == []

    def test_validate_config_invalid(self):
        """Test validate_config with invalid config."""
        from src.core.clamav_config import validate_config

        config = ClamAVConfig(file_path=Path("/test"))
        config.set_value("LogVerbose", "invalid")

        is_valid, errors = validate_config(config)

        assert is_valid is False
        assert len(errors) > 0


class TestBackupConfig:
    """Tests for the backup_config function."""

    def test_backup_config_creates_backup(self, tmp_path):
        """Test backup_config creates a backup file."""
        from src.core.clamav_config import backup_config

        config_file = tmp_path / "test.conf"
        config_file.write_text("LogVerbose yes\n")

        backup_config(str(config_file))

        # Find backup file
        backup_files = list(tmp_path.glob("test.bak.*"))
        assert len(backup_files) == 1
        assert backup_files[0].read_text() == "LogVerbose yes\n"

    def test_backup_config_nonexistent(self, tmp_path):
        """Test backup_config handles nonexistent file."""
        from src.core.clamav_config import backup_config

        # Should not raise exception
        backup_config(str(tmp_path / "nonexistent.conf"))


class TestClamAVConfigToString:
    """Tests for ClamAVConfig.to_string method."""

    def test_to_string_empty_config(self):
        """Test to_string with empty config."""
        config = ClamAVConfig(file_path=Path("/test"))

        result = config.to_string()

        assert result == ""

    def test_to_string_no_raw_lines(self):
        """Test to_string generates from values when no raw lines."""
        config = ClamAVConfig(file_path=Path("/test"))
        config.set_value("LogVerbose", "yes")
        config.set_value("Checks", "24")

        result = config.to_string()

        assert "LogVerbose yes" in result
        assert "Checks 24" in result

    def test_to_string_with_raw_lines(self):
        """Test to_string preserves raw lines structure."""
        config = ClamAVConfig(file_path=Path("/test"))
        config.raw_lines = ["# Comment\n", "LogVerbose yes\n", "\n", "Checks 24\n"]
        config.values["LogVerbose"] = [ClamAVConfigValue(value="no", line_number=2)]
        config.values["Checks"] = [ClamAVConfigValue(value="12", line_number=4)]

        result = config.to_string()

        assert "# Comment" in result
        assert "LogVerbose no" in result
        assert "Checks 12" in result

    def test_to_string_with_new_values(self):
        """Test to_string appends new values without line numbers."""
        config = ClamAVConfig(file_path=Path("/test"))
        config.raw_lines = ["LogVerbose yes\n"]
        config.set_value("NewOption", "value")

        result = config.to_string()

        assert "LogVerbose yes" in result
        assert "NewOption value" in result

    def test_to_string_with_inline_comment(self):
        """Test to_string preserves inline comments."""
        config = ClamAVConfig(file_path=Path("/test"))
        config.raw_lines = ["LogVerbose yes\n"]
        config.values["LogVerbose"] = [
            ClamAVConfigValue(value="no", comment="Changed to no", line_number=1)
        ]

        result = config.to_string()

        assert "LogVerbose no" in result
        assert "# Changed to no" in result
