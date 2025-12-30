# ClamUI Tray Indicator Module
"""
Tray indicator module for ClamUI providing system tray integration.
Uses AyatanaAppIndicator3 for native Linux AppIndicator support.

Note: This module uses GTK3 for menu creation (required by AppIndicator)
while the main application uses GTK4. GTK3 code is isolated to this module.
"""

import logging
from typing import Optional

# GTK3 imports for AppIndicator (isolated from GTK4 main app)
import gi

gi.require_version("Gtk", "3.0")
gi.require_version("AyatanaAppIndicator3", "0.1")

from gi.repository import AyatanaAppIndicator3 as AppIndicator
from gi.repository import Gtk as Gtk3


logger = logging.getLogger(__name__)


class TrayIndicator:
    """
    Manager for system tray indicator.

    Provides a persistent tray icon with status awareness,
    right-click menu for quick actions, and window toggle support.
    Uses AyatanaAppIndicator3 for Linux AppIndicator integration.
    """

    # Icon mapping for different protection states
    ICON_MAP = {
        "protected": "security-high-symbolic",
        "warning": "dialog-warning-symbolic",
        "scanning": "emblem-synchronizing-symbolic",
        "threat": "dialog-error-symbolic",
    }

    # Default fallback icon if custom icon not found
    DEFAULT_ICON = "security-high-symbolic"

    # Application indicator ID
    INDICATOR_ID = "clamui-tray"

    def __init__(self) -> None:
        """
        Initialize the TrayIndicator.

        Creates an AppIndicator instance with a basic menu.
        The indicator is not visible until activate() is called.
        """
        self._indicator: Optional[AppIndicator.Indicator] = None
        self._menu: Optional[Gtk3.Menu] = None
        self._current_status: str = "protected"

        # Create the indicator
        self._create_indicator()

    def _create_indicator(self) -> None:
        """
        Create and configure the AppIndicator instance.
        """
        self._indicator = AppIndicator.Indicator.new(
            self.INDICATOR_ID,
            self.DEFAULT_ICON,
            AppIndicator.IndicatorCategory.APPLICATION_STATUS,
        )

        # Build initial menu (required before activating)
        self._menu = self._build_menu()
        self._indicator.set_menu(self._menu)

        # Set tooltip/title
        self._indicator.set_title("ClamUI")

    def _build_menu(self) -> Gtk3.Menu:
        """
        Build the GTK3 context menu for the indicator.

        Returns:
            GTK3 Menu with placeholder items (actions connected in later subtask)
        """
        menu = Gtk3.Menu()

        # Placeholder items - actions will be connected in subtask 2-2
        quick_scan_item = Gtk3.MenuItem(label="Quick Scan")
        menu.append(quick_scan_item)

        full_scan_item = Gtk3.MenuItem(label="Full Scan")
        menu.append(full_scan_item)

        menu.append(Gtk3.SeparatorMenuItem())

        update_item = Gtk3.MenuItem(label="Update Definitions")
        menu.append(update_item)

        menu.append(Gtk3.SeparatorMenuItem())

        quit_item = Gtk3.MenuItem(label="Quit")
        menu.append(quit_item)

        # Show all menu items
        menu.show_all()

        return menu

    def activate(self) -> None:
        """
        Activate the indicator to make it visible in the system tray.

        Must be called after initialization for the icon to appear.
        """
        if self._indicator is not None:
            self._indicator.set_status(AppIndicator.IndicatorStatus.ACTIVE)
            logger.debug("Tray indicator activated")

    def deactivate(self) -> None:
        """
        Deactivate the indicator to hide it from the system tray.
        """
        if self._indicator is not None:
            self._indicator.set_status(AppIndicator.IndicatorStatus.PASSIVE)
            logger.debug("Tray indicator deactivated")

    def update_status(self, status: str) -> None:
        """
        Update the tray icon based on protection status.

        Args:
            status: One of 'protected', 'warning', 'scanning', 'threat'
        """
        if self._indicator is None:
            return

        icon_name = self.ICON_MAP.get(status, self.DEFAULT_ICON)
        tooltip = f"ClamUI - {status.capitalize()}"

        self._indicator.set_icon_full(icon_name, tooltip)
        self._current_status = status
        logger.debug(f"Tray status updated to: {status}")

    def update_scan_progress(self, percentage: int) -> None:
        """
        Show scan progress percentage in the tray.

        Args:
            percentage: Progress percentage (0-100). Use 0 to clear.
        """
        if self._indicator is None:
            return

        if 0 < percentage <= 100:
            self._indicator.set_label(f"{percentage}%", "")
            # Update icon to scanning state if not already
            if self._current_status != "scanning":
                self.update_status("scanning")
        else:
            # Clear the label when not scanning
            self._indicator.set_label("", "")

    def cleanup(self) -> None:
        """
        Clean up resources and remove the indicator from tray.

        Should be called before application exit to prevent ghost icons.
        """
        self.deactivate()
        self._menu = None
        self._indicator = None
        logger.debug("Tray indicator cleaned up")

    @property
    def is_active(self) -> bool:
        """
        Check if the indicator is currently visible.

        Returns:
            True if indicator is active, False otherwise
        """
        if self._indicator is None:
            return False
        return (
            self._indicator.get_status() == AppIndicator.IndicatorStatus.ACTIVE
        )

    @property
    def current_status(self) -> str:
        """
        Get the current protection status.

        Returns:
            Current status string ('protected', 'warning', 'scanning', 'threat')
        """
        return self._current_status
