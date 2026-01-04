# ClamUI Keyboard Shortcuts Tests
"""
Unit tests for keyboard shortcut functionality.

Tests cover:
- Accelerator registration for all navigation actions
- Accelerator registration for action shortcuts
- Correct action names and accelerator bindings
- Verification that all shortcuts are properly bound
"""

import sys
from unittest import mock

import pytest


def _clear_src_modules():
    """Clear all cached src.* modules to prevent test pollution."""
    modules_to_remove = [mod for mod in sys.modules if mod.startswith("src.")]
    for mod in modules_to_remove:
        del sys.modules[mod]


@pytest.fixture
def app_class(mock_gi_modules):
    """Get ClamUIApp class with mocked dependencies."""
    # Mock additional dependencies
    mock_settings_manager = mock.MagicMock()
    mock_notification_manager = mock.MagicMock()
    mock_profile_manager = mock.MagicMock()

    with mock.patch.dict(
        sys.modules,
        {
            "src.core.settings_manager": mock.MagicMock(SettingsManager=mock_settings_manager),
            "src.core.notification_manager": mock.MagicMock(
                NotificationManager=mock_notification_manager
            ),
            "src.profiles.profile_manager": mock.MagicMock(ProfileManager=mock_profile_manager),
        },
    ):
        # Clear any cached import
        if "src.app" in sys.modules:
            del sys.modules["src.app"]

        from src.app import ClamUIApp

        yield ClamUIApp

    # Clear all src.* modules after test
    _clear_src_modules()


@pytest.fixture
def mock_app(app_class, mock_gi_modules):
    """Create a mock ClamUIApp instance for testing."""
    # Create instance without calling __init__
    app = object.__new__(app_class)

    # Mock Gio module for actions
    gio = mock_gi_modules["gio"]

    # Set up required attributes
    app._settings_manager = mock.MagicMock()
    app._notification_manager = mock.MagicMock()
    app._profile_manager = mock.MagicMock()
    app._scan_view = None
    app._update_view = None
    app._logs_view = None
    app._components_view = None
    app._statistics_view = None
    app._quarantine_view = None
    app._current_view = None
    app._tray_indicator = None
    app._first_activation = True

    # Mock the application methods we need
    app.add_action = mock.MagicMock()
    app.set_accels_for_action = mock.MagicMock()

    return app


class TestNavigationAccelerators:
    """Tests for navigation keyboard accelerators."""

    def test_show_scan_accelerator(self, mock_app, mock_gi_modules):
        """Test show-scan action has Ctrl+1 accelerator."""
        # Call _setup_actions
        mock_app._setup_actions()

        # Verify set_accels_for_action was called with correct parameters
        mock_app.set_accels_for_action.assert_any_call("app.show-scan", ["<Control>1"])

    def test_show_update_accelerator(self, mock_app, mock_gi_modules):
        """Test show-update action has Ctrl+2 accelerator."""
        mock_app._setup_actions()

        mock_app.set_accels_for_action.assert_any_call("app.show-update", ["<Control>2"])

    def test_show_logs_accelerator(self, mock_app, mock_gi_modules):
        """Test show-logs action has Ctrl+3 accelerator."""
        mock_app._setup_actions()

        mock_app.set_accels_for_action.assert_any_call("app.show-logs", ["<Control>3"])

    def test_show_components_accelerator(self, mock_app, mock_gi_modules):
        """Test show-components action has Ctrl+4 accelerator."""
        mock_app._setup_actions()

        mock_app.set_accels_for_action.assert_any_call("app.show-components", ["<Control>4"])

    def test_show_quarantine_accelerator(self, mock_app, mock_gi_modules):
        """Test show-quarantine action has Ctrl+5 accelerator."""
        mock_app._setup_actions()

        mock_app.set_accels_for_action.assert_any_call("app.show-quarantine", ["<Control>5"])

    def test_show_statistics_accelerator(self, mock_app, mock_gi_modules):
        """Test show-statistics action has Ctrl+6 accelerator."""
        mock_app._setup_actions()

        mock_app.set_accels_for_action.assert_any_call("app.show-statistics", ["<Control>6"])


class TestActionAccelerators:
    """Tests for action keyboard accelerators."""

    def test_quit_accelerator(self, mock_app, mock_gi_modules):
        """Test quit action has Ctrl+Q accelerator."""
        mock_app._setup_actions()

        mock_app.set_accels_for_action.assert_any_call("app.quit", ["<Control>q"])

    def test_preferences_accelerator(self, mock_app, mock_gi_modules):
        """Test preferences action has Ctrl+, accelerator."""
        mock_app._setup_actions()

        mock_app.set_accels_for_action.assert_any_call("app.preferences", ["<Control>comma"])

    def test_start_scan_accelerator(self, mock_app, mock_gi_modules):
        """Test start-scan action has F5 accelerator."""
        mock_app._setup_actions()

        mock_app.set_accels_for_action.assert_any_call("app.start-scan", ["F5"])

    def test_start_update_accelerator(self, mock_app, mock_gi_modules):
        """Test start-update action has F6 accelerator."""
        mock_app._setup_actions()

        mock_app.set_accels_for_action.assert_any_call("app.start-update", ["F6"])


class TestActionRegistration:
    """Tests for action registration in _setup_actions."""

    def test_all_navigation_actions_registered(self, mock_app, mock_gi_modules):
        """Test that all navigation actions are registered."""
        # Mock SimpleAction.new to track action creation
        gio = mock_gi_modules["gio"]
        mock_action = mock.MagicMock()
        gio.SimpleAction.new.return_value = mock_action

        mock_app._setup_actions()

        # Verify all navigation actions were created
        navigation_actions = [
            "show-scan",
            "show-update",
            "show-logs",
            "show-components",
            "show-quarantine",
            "show-statistics",
        ]

        for action_name in navigation_actions:
            gio.SimpleAction.new.assert_any_call(action_name, None)

    def test_all_action_shortcuts_registered(self, mock_app, mock_gi_modules):
        """Test that all action shortcuts are registered."""
        gio = mock_gi_modules["gio"]
        mock_action = mock.MagicMock()
        gio.SimpleAction.new.return_value = mock_action

        mock_app._setup_actions()

        # Verify all action shortcuts were created
        action_shortcuts = ["quit", "about", "preferences", "start-scan", "start-update"]

        for action_name in action_shortcuts:
            gio.SimpleAction.new.assert_any_call(action_name, None)

    def test_all_actions_added_to_app(self, mock_app, mock_gi_modules):
        """Test that all created actions are added to the application."""
        gio = mock_gi_modules["gio"]
        mock_action = mock.MagicMock()
        gio.SimpleAction.new.return_value = mock_action

        mock_app._setup_actions()

        # Should have 11 actions total
        # 6 navigation + 5 actions (quit, about, preferences, start-scan, start-update)
        expected_action_count = 11

        # Verify add_action was called the expected number of times
        assert mock_app.add_action.call_count == expected_action_count

    def test_actions_connected_to_handlers(self, mock_app, mock_gi_modules):
        """Test that actions are connected to their handler methods."""
        gio = mock_gi_modules["gio"]
        mock_action = mock.MagicMock()
        gio.SimpleAction.new.return_value = mock_action

        # Mock the handler methods
        mock_app._on_quit = mock.MagicMock()
        mock_app._on_about = mock.MagicMock()
        mock_app._on_preferences = mock.MagicMock()
        mock_app._on_show_scan = mock.MagicMock()
        mock_app._on_show_update = mock.MagicMock()
        mock_app._on_show_logs = mock.MagicMock()
        mock_app._on_show_components = mock.MagicMock()
        mock_app._on_show_quarantine = mock.MagicMock()
        mock_app._on_show_statistics = mock.MagicMock()
        mock_app._on_start_scan = mock.MagicMock()
        mock_app._on_start_update = mock.MagicMock()

        mock_app._setup_actions()

        # Verify connect was called on each action
        # 11 actions total should all have connect called
        assert mock_action.connect.call_count == 11


class TestAcceleratorCount:
    """Tests for verifying all accelerators are registered."""

    def test_all_accelerators_registered(self, mock_app, mock_gi_modules):
        """Test that all keyboard accelerators are registered."""
        mock_app._setup_actions()

        # Expected accelerators:
        # - Ctrl+1 through Ctrl+6 (6 navigation)
        # - Ctrl+Q (quit)
        # - Ctrl+, (preferences)
        # - F5 (start-scan)
        # - F6 (start-update)
        # Total: 10 accelerators
        expected_accelerator_count = 10

        assert mock_app.set_accels_for_action.call_count == expected_accelerator_count

    def test_no_duplicate_accelerators(self, mock_app, mock_gi_modules):
        """Test that no accelerator is bound to multiple actions."""
        mock_app._setup_actions()

        # Get all accelerator calls
        calls = mock_app.set_accels_for_action.call_args_list

        # Extract accelerators (second argument of each call)
        accelerators = [call[0][1][0] for call in calls]

        # Check for duplicates
        assert len(accelerators) == len(set(accelerators)), "Duplicate accelerators detected"

    def test_accelerator_format_consistency(self, mock_app, mock_gi_modules):
        """Test that all accelerators use consistent format."""
        mock_app._setup_actions()

        # Get all accelerator calls
        calls = mock_app.set_accels_for_action.call_args_list

        # Check that all accelerators are in list format
        for call in calls:
            accelerator_list = call[0][1]
            assert isinstance(accelerator_list, list), "Accelerator must be in list format"
            assert len(accelerator_list) == 1, "Each action should have exactly one accelerator"


class TestAcceleratorBindings:
    """Tests for specific accelerator to action bindings."""

    def test_navigation_accelerators_mapping(self, mock_app, mock_gi_modules):
        """Test correct mapping of navigation accelerators to actions."""
        mock_app._setup_actions()

        # Expected mappings
        expected_mappings = {
            "app.show-scan": "<Control>1",
            "app.show-update": "<Control>2",
            "app.show-logs": "<Control>3",
            "app.show-components": "<Control>4",
            "app.show-quarantine": "<Control>5",
            "app.show-statistics": "<Control>6",
        }

        # Verify each mapping
        for action, accelerator in expected_mappings.items():
            mock_app.set_accels_for_action.assert_any_call(action, [accelerator])

    def test_action_accelerators_mapping(self, mock_app, mock_gi_modules):
        """Test correct mapping of action accelerators to actions."""
        mock_app._setup_actions()

        # Expected mappings
        expected_mappings = {
            "app.quit": "<Control>q",
            "app.preferences": "<Control>comma",
            "app.start-scan": "F5",
            "app.start-update": "F6",
        }

        # Verify each mapping
        for action, accelerator in expected_mappings.items():
            mock_app.set_accels_for_action.assert_any_call(action, [accelerator])
