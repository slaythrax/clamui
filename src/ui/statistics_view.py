# ClamUI Statistics View
"""
Statistics dashboard component for ClamUI displaying scan metrics and protection status.
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib

from ..core.statistics_calculator import (
    StatisticsCalculator,
    ScanStatistics,
    ProtectionStatus,
    Timeframe,
    ProtectionLevel,
)


class StatisticsView(Gtk.Box):
    """
    Statistics dashboard component for ClamUI.

    Provides the statistics viewing interface with:
    - Summary cards (total scans, files scanned, threats detected)
    - Timeframe selector (daily/weekly/monthly/all-time)
    - Protection status indicator
    - Average scan duration display
    - Quick action buttons for common operations

    Uses Adw.PreferencesGroup for consistent styling with other views.
    """

    def __init__(self, **kwargs):
        """
        Initialize the statistics view.

        Args:
            **kwargs: Additional arguments passed to parent
        """
        super().__init__(orientation=Gtk.Orientation.VERTICAL, **kwargs)

        # Initialize statistics calculator
        self._calculator = StatisticsCalculator()

        # Current selected timeframe
        self._current_timeframe: str = Timeframe.WEEKLY.value

        # Loading state
        self._is_loading = False

        # Current statistics and protection status
        self._current_stats: ScanStatistics | None = None
        self._current_protection: ProtectionStatus | None = None

        # Quick action callback (for triggering scans from parent)
        self._on_quick_scan_requested = None

        # Set up the UI
        self._setup_ui()

        # Load statistics on startup asynchronously
        GLib.idle_add(self._load_statistics_async)

    def _setup_ui(self):
        """Set up the statistics view UI layout."""
        self.set_margin_top(24)
        self.set_margin_bottom(24)
        self.set_margin_start(24)
        self.set_margin_end(24)
        self.set_spacing(18)

        # Create scrollable container for the entire view
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)

        # Main content container
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        content_box.set_spacing(18)

        # Create the protection status section
        self._create_protection_status_section(content_box)

        # Create the timeframe selector section
        self._create_timeframe_section(content_box)

        # Create the statistics cards section
        self._create_statistics_section(content_box)

        # Create the quick actions section
        self._create_quick_actions_section(content_box)

        scrolled.set_child(content_box)
        self.append(scrolled)

    def _create_protection_status_section(self, parent: Gtk.Box):
        """
        Create the protection status indicator section.

        Args:
            parent: The parent container to add the section to
        """
        # Protection status group
        status_group = Adw.PreferencesGroup()
        status_group.set_title("Protection Status")
        status_group.set_description("Current system security posture")

        # Header box with refresh button
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        header_box.set_halign(Gtk.Align.END)

        # Loading spinner (hidden by default)
        self._status_spinner = Gtk.Spinner()
        self._status_spinner.set_visible(False)

        # Refresh button
        refresh_button = Gtk.Button()
        refresh_button.set_icon_name("view-refresh-symbolic")
        refresh_button.set_tooltip_text("Refresh statistics")
        refresh_button.add_css_class("flat")
        refresh_button.connect("clicked", self._on_refresh_clicked)
        self._refresh_button = refresh_button

        header_box.append(self._status_spinner)
        header_box.append(refresh_button)
        status_group.set_header_suffix(header_box)

        # Protection status row
        self._protection_row = Adw.ActionRow()
        self._protection_row.set_title("System Status")
        self._protection_row.set_subtitle("Checking...")
        self._protection_row.set_icon_name("dialog-question-symbolic")

        # Status badge
        self._status_badge = Gtk.Label()
        self._status_badge.set_label("Unknown")
        self._status_badge.add_css_class("dim-label")
        self._status_badge.set_valign(Gtk.Align.CENTER)
        self._protection_row.add_suffix(self._status_badge)

        status_group.add(self._protection_row)

        # Last scan row
        self._last_scan_row = Adw.ActionRow()
        self._last_scan_row.set_title("Last Scan")
        self._last_scan_row.set_subtitle("No scans recorded")
        self._last_scan_row.set_icon_name("document-open-recent-symbolic")

        status_group.add(self._last_scan_row)

        parent.append(status_group)

    def _create_timeframe_section(self, parent: Gtk.Box):
        """
        Create the timeframe selector section.

        Args:
            parent: The parent container to add the section to
        """
        # Timeframe selector group
        timeframe_group = Adw.PreferencesGroup()
        timeframe_group.set_title("Timeframe")
        timeframe_group.set_description("Select the time period for statistics")

        # Timeframe button box
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        button_box.set_halign(Gtk.Align.CENTER)
        button_box.set_spacing(6)
        button_box.set_margin_top(6)
        button_box.set_margin_bottom(6)
        button_box.add_css_class("linked")

        # Create timeframe toggle buttons
        self._timeframe_buttons = {}

        timeframes = [
            (Timeframe.DAILY.value, "Day"),
            (Timeframe.WEEKLY.value, "Week"),
            (Timeframe.MONTHLY.value, "Month"),
            (Timeframe.ALL.value, "All Time"),
        ]

        for timeframe, label in timeframes:
            button = Gtk.ToggleButton()
            button.set_label(label)
            button.connect("toggled", self._on_timeframe_toggled, timeframe)
            self._timeframe_buttons[timeframe] = button
            button_box.append(button)

        # Set default active button
        self._timeframe_buttons[self._current_timeframe].set_active(True)

        timeframe_group.add(button_box)
        parent.append(timeframe_group)

    def _create_statistics_section(self, parent: Gtk.Box):
        """
        Create the statistics cards section.

        Args:
            parent: The parent container to add the section to
        """
        # Statistics group
        stats_group = Adw.PreferencesGroup()
        stats_group.set_title("Scan Statistics")
        stats_group.set_description("Aggregated metrics for the selected timeframe")
        self._stats_group = stats_group

        # Total scans row
        self._total_scans_row = Adw.ActionRow()
        self._total_scans_row.set_title("Total Scans")
        self._total_scans_row.set_subtitle("Number of scans performed")
        self._total_scans_row.set_icon_name("folder-saved-search-symbolic")

        self._total_scans_label = Gtk.Label()
        self._total_scans_label.set_label("0")
        self._total_scans_label.add_css_class("title-1")
        self._total_scans_label.set_valign(Gtk.Align.CENTER)
        self._total_scans_row.add_suffix(self._total_scans_label)

        stats_group.add(self._total_scans_row)

        # Files scanned row
        self._files_scanned_row = Adw.ActionRow()
        self._files_scanned_row.set_title("Files Scanned")
        self._files_scanned_row.set_subtitle("Total files checked")
        self._files_scanned_row.set_icon_name("document-open-symbolic")

        self._files_scanned_label = Gtk.Label()
        self._files_scanned_label.set_label("0")
        self._files_scanned_label.add_css_class("title-1")
        self._files_scanned_label.set_valign(Gtk.Align.CENTER)
        self._files_scanned_row.add_suffix(self._files_scanned_label)

        stats_group.add(self._files_scanned_row)

        # Threats detected row
        self._threats_row = Adw.ActionRow()
        self._threats_row.set_title("Threats Detected")
        self._threats_row.set_subtitle("Malware and suspicious files found")
        self._threats_row.set_icon_name("dialog-warning-symbolic")

        self._threats_label = Gtk.Label()
        self._threats_label.set_label("0")
        self._threats_label.add_css_class("title-1")
        self._threats_label.set_valign(Gtk.Align.CENTER)
        self._threats_row.add_suffix(self._threats_label)

        stats_group.add(self._threats_row)

        # Clean scans row
        self._clean_scans_row = Adw.ActionRow()
        self._clean_scans_row.set_title("Clean Scans")
        self._clean_scans_row.set_subtitle("Scans with no threats found")
        self._clean_scans_row.set_icon_name("emblem-ok-symbolic")

        self._clean_scans_label = Gtk.Label()
        self._clean_scans_label.set_label("0")
        self._clean_scans_label.add_css_class("title-1")
        self._clean_scans_label.set_valign(Gtk.Align.CENTER)
        self._clean_scans_row.add_suffix(self._clean_scans_label)

        stats_group.add(self._clean_scans_row)

        # Average duration row
        self._duration_row = Adw.ActionRow()
        self._duration_row.set_title("Average Scan Duration")
        self._duration_row.set_subtitle("Mean time per scan")
        self._duration_row.set_icon_name("preferences-system-time-symbolic")

        self._duration_label = Gtk.Label()
        self._duration_label.set_label("--")
        self._duration_label.add_css_class("title-2")
        self._duration_label.set_valign(Gtk.Align.CENTER)
        self._duration_row.add_suffix(self._duration_label)

        stats_group.add(self._duration_row)

        parent.append(stats_group)

    def _create_quick_actions_section(self, parent: Gtk.Box):
        """
        Create the quick actions section.

        Args:
            parent: The parent container to add the section to
        """
        # Quick actions group
        actions_group = Adw.PreferencesGroup()
        actions_group.set_title("Quick Actions")
        actions_group.set_description("Common scanning operations")

        # Quick scan row
        quick_scan_row = Adw.ActionRow()
        quick_scan_row.set_title("Quick Scan")
        quick_scan_row.set_subtitle("Scan your home directory")
        quick_scan_row.set_icon_name("media-playback-start-symbolic")
        quick_scan_row.set_activatable(True)
        quick_scan_row.connect("activated", self._on_quick_scan_clicked)

        # Add chevron to indicate it's activatable
        chevron = Gtk.Image.new_from_icon_name("go-next-symbolic")
        chevron.add_css_class("dim-label")
        quick_scan_row.add_suffix(chevron)

        actions_group.add(quick_scan_row)

        # View logs row
        view_logs_row = Adw.ActionRow()
        view_logs_row.set_title("View Scan Logs")
        view_logs_row.set_subtitle("See detailed scan history")
        view_logs_row.set_icon_name("document-open-recent-symbolic")
        view_logs_row.set_activatable(True)
        view_logs_row.connect("activated", self._on_view_logs_clicked)

        chevron2 = Gtk.Image.new_from_icon_name("go-next-symbolic")
        chevron2.add_css_class("dim-label")
        view_logs_row.add_suffix(chevron2)

        actions_group.add(view_logs_row)

        parent.append(actions_group)

    def _load_statistics_async(self) -> bool:
        """
        Load statistics asynchronously.

        Returns:
            False to prevent GLib.idle_add from repeating
        """
        if self._is_loading:
            return False

        self._set_loading_state(True)

        # Load statistics in idle callback to not block UI
        GLib.idle_add(self._perform_load)

        return False

    def _perform_load(self) -> bool:
        """
        Perform the actual statistics loading.

        Returns:
            False to prevent GLib.idle_add from repeating
        """
        try:
            # Get statistics for current timeframe
            self._current_stats = self._calculator.get_statistics(self._current_timeframe)

            # Get protection status
            self._current_protection = self._calculator.get_protection_status()

            # Update UI with loaded data
            self._update_statistics_display()
            self._update_protection_display()

        except Exception:
            # Handle errors gracefully
            self._show_empty_state()
        finally:
            self._set_loading_state(False)

        return False

    def _update_statistics_display(self):
        """Update the statistics display with current data."""
        if self._current_stats is None:
            self._show_empty_state()
            return

        stats = self._current_stats

        # Update total scans
        self._total_scans_label.set_label(str(stats.total_scans))

        # Update files scanned
        self._files_scanned_label.set_label(self._format_number(stats.files_scanned))

        # Update threats detected
        self._threats_label.set_label(str(stats.threats_detected))

        # Update styling based on threat count
        if stats.threats_detected > 0:
            self._threats_label.add_css_class("error")
        else:
            self._threats_label.remove_css_class("error")

        # Update clean scans
        self._clean_scans_label.set_label(str(stats.clean_scans))

        # Update average duration
        if stats.average_duration > 0:
            self._duration_label.set_label(self._format_duration(stats.average_duration))
        else:
            self._duration_label.set_label("--")

        # Update group description with date range
        if stats.start_date and stats.end_date:
            try:
                from datetime import datetime
                start = datetime.fromisoformat(stats.start_date)
                end = datetime.fromisoformat(stats.end_date)
                date_range = f"{start.strftime('%b %d')} - {end.strftime('%b %d, %Y')}"
                self._stats_group.set_description(f"Statistics for: {date_range}")
            except (ValueError, AttributeError):
                self._stats_group.set_description("Aggregated metrics for the selected timeframe")
        else:
            self._stats_group.set_description("Aggregated metrics for all time")

    def _update_protection_display(self):
        """Update the protection status display."""
        if self._current_protection is None:
            self._protection_row.set_subtitle("Unable to determine status")
            self._protection_row.set_icon_name("dialog-question-symbolic")
            self._status_badge.set_label("Unknown")
            return

        status = self._current_protection

        # Update protection row
        self._protection_row.set_subtitle(status.message)

        # Update icon and badge based on protection level
        if status.level == ProtectionLevel.PROTECTED.value:
            self._protection_row.set_icon_name("emblem-ok-symbolic")
            self._status_badge.set_label("Protected")
            self._status_badge.remove_css_class("warning")
            self._status_badge.remove_css_class("error")
            self._status_badge.add_css_class("success")
        elif status.level == ProtectionLevel.AT_RISK.value:
            self._protection_row.set_icon_name("dialog-warning-symbolic")
            self._status_badge.set_label("At Risk")
            self._status_badge.remove_css_class("success")
            self._status_badge.remove_css_class("error")
            self._status_badge.add_css_class("warning")
        elif status.level == ProtectionLevel.UNPROTECTED.value:
            self._protection_row.set_icon_name("dialog-error-symbolic")
            self._status_badge.set_label("Unprotected")
            self._status_badge.remove_css_class("success")
            self._status_badge.remove_css_class("warning")
            self._status_badge.add_css_class("error")
        else:
            self._protection_row.set_icon_name("dialog-question-symbolic")
            self._status_badge.set_label("Unknown")
            self._status_badge.remove_css_class("success")
            self._status_badge.remove_css_class("warning")
            self._status_badge.remove_css_class("error")

        # Update last scan row
        if status.last_scan_timestamp:
            try:
                from datetime import datetime
                last_scan = datetime.fromisoformat(
                    status.last_scan_timestamp.replace("Z", "+00:00").split("+")[0]
                )
                time_str = last_scan.strftime("%Y-%m-%d %H:%M")

                if status.last_scan_age_hours is not None:
                    if status.last_scan_age_hours < 1:
                        age_str = "less than an hour ago"
                    elif status.last_scan_age_hours < 24:
                        hours = int(status.last_scan_age_hours)
                        age_str = f"{hours} hour{'s' if hours != 1 else ''} ago"
                    elif status.last_scan_age_hours < 24 * 7:
                        days = int(status.last_scan_age_hours / 24)
                        age_str = f"{days} day{'s' if days != 1 else ''} ago"
                    else:
                        weeks = int(status.last_scan_age_hours / (24 * 7))
                        age_str = f"{weeks} week{'s' if weeks != 1 else ''} ago"

                    self._last_scan_row.set_subtitle(f"{time_str} ({age_str})")
                else:
                    self._last_scan_row.set_subtitle(time_str)
            except (ValueError, AttributeError):
                self._last_scan_row.set_subtitle(status.last_scan_timestamp)
        else:
            self._last_scan_row.set_subtitle("No scans recorded")

    def _show_empty_state(self):
        """Display empty state when no statistics are available."""
        self._total_scans_label.set_label("0")
        self._files_scanned_label.set_label("0")
        self._threats_label.set_label("0")
        self._clean_scans_label.set_label("0")
        self._duration_label.set_label("--")

        self._protection_row.set_subtitle("No scan history available")
        self._protection_row.set_icon_name("dialog-information-symbolic")
        self._status_badge.set_label("No Data")
        self._status_badge.remove_css_class("success")
        self._status_badge.remove_css_class("warning")
        self._status_badge.remove_css_class("error")

        self._last_scan_row.set_subtitle("Run a scan to see statistics")

        self._stats_group.set_description("Run your first scan to see statistics here")

    def _format_number(self, number: int) -> str:
        """
        Format a number with thousand separators.

        Args:
            number: Number to format

        Returns:
            Formatted string (e.g., "1,234")
        """
        return f"{number:,}"

    def _format_duration(self, seconds: float) -> str:
        """
        Format a duration in seconds to a human-readable string.

        Args:
            seconds: Duration in seconds

        Returns:
            Formatted string (e.g., "2m 30s")
        """
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            remaining_seconds = int(seconds % 60)
            return f"{minutes}m {remaining_seconds}s"
        else:
            hours = int(seconds // 3600)
            remaining_minutes = int((seconds % 3600) // 60)
            return f"{hours}h {remaining_minutes}m"

    def _set_loading_state(self, is_loading: bool):
        """
        Update UI to reflect loading state.

        Args:
            is_loading: Whether statistics are currently being loaded
        """
        self._is_loading = is_loading

        if is_loading:
            self._status_spinner.set_visible(True)
            self._status_spinner.start()
            self._refresh_button.set_sensitive(False)
        else:
            self._status_spinner.stop()
            self._status_spinner.set_visible(False)
            self._refresh_button.set_sensitive(True)

    def _on_refresh_clicked(self, button: Gtk.Button):
        """Handle refresh button click."""
        self._load_statistics_async()

    def _on_timeframe_toggled(self, button: Gtk.ToggleButton, timeframe: str):
        """
        Handle timeframe button toggle.

        Args:
            button: The toggled button
            timeframe: The timeframe value associated with the button
        """
        if not button.get_active():
            return

        # Deactivate other buttons
        for tf, btn in self._timeframe_buttons.items():
            if tf != timeframe:
                btn.set_active(False)

        # Update current timeframe and reload
        self._current_timeframe = timeframe
        self._load_statistics_async()

    def _on_quick_scan_clicked(self, row: Adw.ActionRow):
        """Handle quick scan action click."""
        if self._on_quick_scan_requested:
            self._on_quick_scan_requested()
        else:
            # Try to activate the show-scan action
            app = self.get_root()
            if app and hasattr(app, 'activate_action'):
                app.activate_action('app.show-scan', None)

    def _on_view_logs_clicked(self, row: Adw.ActionRow):
        """Handle view logs action click."""
        # Try to activate the show-logs action
        app = self.get_root()
        if app and hasattr(app, 'activate_action'):
            app.activate_action('app.show-logs', None)

    def set_quick_scan_callback(self, callback):
        """
        Set callback for quick scan requests.

        Args:
            callback: Callable to invoke when quick scan is requested
        """
        self._on_quick_scan_requested = callback

    def refresh_statistics(self):
        """
        Public method to refresh the statistics display.

        Can be called externally when scans complete.
        """
        GLib.idle_add(self._load_statistics_async)

    @property
    def calculator(self) -> StatisticsCalculator:
        """
        Get the statistics calculator instance.

        Returns:
            The StatisticsCalculator instance used by this view
        """
        return self._calculator
