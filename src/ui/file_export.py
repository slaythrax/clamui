# ClamUI File Export Helper
"""
Reusable file export dialog helper for GTK4 applications.

Provides a generic export workflow that handles:
- FileDialog setup with filters
- Async file selection callback
- File writing with error handling
- Toast notifications for success/failure

This eliminates duplication across export operations for different formats
(text, CSV, JSON, etc.) by extracting the common dialog/callback pattern.
"""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gio, GLib, Gtk


@dataclass
class FileFilter:
    """Configuration for a file type filter in the export dialog."""

    name: str
    """Display name for the filter (e.g., "CSV Files")"""

    extension: str
    """File extension without the dot (e.g., "csv")"""

    mime_type: str | None = None
    """MIME type for the filter (e.g., "text/csv")"""


class FileExportHelper:
    """
    Helper class for file export operations with GTK4 FileDialog.

    Encapsulates the common pattern of:
    1. Creating a FileDialog with title and filters
    2. Setting a default filename with timestamp
    3. Handling async file selection callback
    4. Writing content with error handling
    5. Showing toast notifications

    This eliminates ~80 lines of duplicated code per export format.

    Example usage:
        def export_to_csv(self, button):
            helper = FileExportHelper(
                parent_widget=self,
                dialog_title="Export to CSV",
                filename_prefix="clamui_export",
                file_filter=FileFilter(name="CSV Files", extension="csv", mime_type="text/csv"),
                content_generator=lambda: self._format_as_csv(),
            )
            helper.show_save_dialog()
    """

    def __init__(
        self,
        parent_widget: Gtk.Widget,
        dialog_title: str,
        filename_prefix: str,
        file_filter: FileFilter,
        content_generator: Callable[[], str],
        success_message: str | None = None,
        toast_manager: Adw.ToastOverlay | None = None,
    ):
        """
        Initialize the file export helper.

        Args:
            parent_widget: Widget to get the parent window from (for dialog transient)
            dialog_title: Title for the save dialog (e.g., "Export Log Details")
            filename_prefix: Prefix for the generated filename (timestamp will be appended)
            file_filter: FileFilter configuration for the dialog
            content_generator: Callable that returns the content string to write.
                               Called at write time, not at dialog creation.
            success_message: Optional custom success message. If None, uses
                            "Exported to {filename}".
            toast_manager: Optional ToastOverlay for notifications. If None,
                          attempts to find one via parent_widget.get_root().
        """
        self._parent_widget = parent_widget
        self._dialog_title = dialog_title
        self._filename_prefix = filename_prefix
        self._file_filter = file_filter
        self._content_generator = content_generator
        self._success_message = success_message
        self._toast_manager = toast_manager

    def show_save_dialog(self) -> None:
        """
        Open the file save dialog.

        Creates a FileDialog with the configured title, filters, and default
        filename, then opens it asynchronously. The callback will handle
        file writing and notifications.
        """
        dialog = Gtk.FileDialog()
        dialog.set_title(self._dialog_title)

        # Generate default filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        extension = self._file_filter.extension
        dialog.set_initial_name(f"{self._filename_prefix}_{timestamp}.{extension}")

        # Set up file filter
        gtk_filter = Gtk.FileFilter()
        gtk_filter.set_name(self._file_filter.name)
        if self._file_filter.mime_type:
            gtk_filter.add_mime_type(self._file_filter.mime_type)
        gtk_filter.add_pattern(f"*.{extension}")

        filters = Gio.ListStore.new(Gtk.FileFilter)
        filters.append(gtk_filter)
        dialog.set_filters(filters)
        dialog.set_default_filter(gtk_filter)

        # Get the parent window
        window = self._parent_widget.get_root()

        # Open save dialog
        dialog.save(window, None, self._on_file_selected)

    def _on_file_selected(self, dialog: Gtk.FileDialog, result: Gio.AsyncResult) -> None:
        """
        Handle file selection result.

        Writes content to the selected file with proper error handling
        and shows toast notifications.

        Args:
            dialog: The FileDialog that was used
            result: The async result from the save dialog
        """
        try:
            file = dialog.save_finish(result)
            if file is None:
                return  # User cancelled

            file_path = file.get_path()
            if file_path is None:
                self._show_toast("Invalid file path selected", is_error=True)
                return

            # Ensure correct extension
            extension = self._file_filter.extension
            if not file_path.endswith(f".{extension}"):
                file_path += f".{extension}"

            # Generate content
            content = self._content_generator()

            # Write to file
            with open(file_path, "w", encoding="utf-8", newline="") as f:
                f.write(content)

            # Show success feedback
            import os

            filename = os.path.basename(file_path)
            if self._success_message:
                message = self._success_message
            else:
                message = f"Exported to {filename}"
            self._show_toast(message)

        except GLib.Error:
            # User cancelled the dialog
            pass
        except PermissionError:
            self._show_toast("Permission denied - cannot write to selected location", is_error=True)
        except OSError as e:
            self._show_toast(f"Error writing file: {str(e)}", is_error=True)

    def _show_toast(self, message: str, is_error: bool = False) -> None:
        """
        Show a toast notification.

        Args:
            message: The message to display
            is_error: Whether this is an error message (currently unused but
                     available for future styling)
        """
        # First try the explicit toast_manager
        if self._toast_manager is not None:
            toast = Adw.Toast.new(message)
            self._toast_manager.add_toast(toast)
            return

        # Fall back to finding add_toast on the root window
        window = self._parent_widget.get_root()
        if hasattr(window, "add_toast"):
            toast = Adw.Toast.new(message)
            window.add_toast(toast)


# Pre-defined file filters for common export formats
TEXT_FILTER = FileFilter(name="Text Files", extension="txt", mime_type="text/plain")
CSV_FILTER = FileFilter(name="CSV Files", extension="csv", mime_type="text/csv")
JSON_FILTER = FileFilter(name="JSON Files", extension="json", mime_type="application/json")
