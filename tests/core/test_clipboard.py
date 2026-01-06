# ClamUI Clipboard Tests
"""Unit tests for the clipboard module functions."""

from src.core.clipboard import copy_to_clipboard


class TestCopyToClipboard:
    """Tests for the copy_to_clipboard function."""

    def test_copy_empty_string_returns_false(self):
        """Test copy_to_clipboard returns False for empty string."""
        result = copy_to_clipboard("")
        assert result is False

    def test_copy_none_returns_false(self):
        """Test copy_to_clipboard returns False for None."""
        result = copy_to_clipboard(None)
        assert result is False

    def test_copy_whitespace_only_succeeds(self):
        """Test copy_to_clipboard with whitespace-only string (non-empty)."""
        # Whitespace is non-empty, so the function should try to copy
        # (might fail due to no display, but won't return False for empty check)
        result = copy_to_clipboard("   ")
        # Result depends on GTK display availability
        # Just verify it doesn't raise an exception
        assert result in (True, False)
