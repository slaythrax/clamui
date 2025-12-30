# ClamUI

A modern Linux desktop application that provides a graphical user interface for the ClamAV antivirus command-line tool. Built with PyGObject, GTK4, and Adwaita for a native GNOME appearance.

## Features

- **Folder/File Selection**: Select files or directories to scan using the native GTK4 file dialog
- **Async Scanning**: Scans run in the background, keeping the UI responsive
- **Results Display**: Clear, readable display of scan results
- **ClamAV Detection**: Graceful handling when ClamAV is not installed
- **Modern UI**: Native Adwaita styling with proper GNOME integration
- **File Manager Integration**: Right-click "Scan with ClamUI" option in Nautilus, Dolphin, and Nemo

## File Manager Context Menu Integration

ClamUI provides a right-click context menu option in file managers (Nautilus, Dolphin, Nemo) for quick scanning.

### Installing the Context Menu

#### GNOME (Nautilus) and KDE (Dolphin)

1. **Copy the desktop file to your applications directory**:
   ```bash
   cp com.github.clamui.desktop ~/.local/share/applications/
   ```

2. **Update the desktop database**:
   ```bash
   update-desktop-database ~/.local/share/applications
   ```

3. **Restart your file manager** (to reload the desktop file):
   ```bash
   # For GNOME (Nautilus):
   nautilus -q

   # For KDE (Dolphin):
   killall dolphin
   ```

4. **Verify**: Right-click any file or folder in your file manager. You should see "Scan with ClamUI" in the context menu.

#### Cinnamon (Nemo)

Nemo uses its own action format for context menu extensions.

1. **Create the Nemo actions directory** (if it doesn't exist):
   ```bash
   mkdir -p ~/.local/share/nemo/actions
   ```

2. **Copy the Nemo action file**:
   ```bash
   cp com.github.clamui.nemo_action ~/.local/share/nemo/actions/
   ```

3. **Restart Nemo** (to reload actions):
   ```bash
   nemo -q
   ```

4. **Verify**: Right-click any file or folder in Nemo. You should see "Scan with ClamUI" in the context menu.

### Using the Context Menu

- **Single file**: Right-click a file and select "Scan with ClamUI" to scan it
- **Folder**: Right-click a folder to recursively scan all its contents
- **Multiple selection**: Select multiple files/folders, right-click, and scan all at once

### Flatpak Users

If you installed ClamUI via Flatpak, the context menu integration is included automatically. The Flatpak manifest includes the necessary filesystem permissions (`--filesystem=host:ro`) to access files for scanning.

## Requirements

### System Dependencies

ClamUI requires the following system packages (Ubuntu/Debian):

```bash
# GTK4 and Adwaita runtime libraries
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-adw-1 libadwaita-1-dev

# Build dependencies (required for pip install)
sudo apt install libgirepository-2.0-dev libcairo2-dev pkg-config python3-dev
# On Ubuntu < 24.04, use: libgirepository1.0-dev instead of libgirepository-2.0-dev

# ClamAV antivirus
sudo apt install clamav
```

For other distributions:
- **Fedora**: `sudo dnf install python3-gobject python3-gobject-devel gtk4 libadwaita gobject-introspection-devel cairo-gobject-devel clamav`
- **Arch**: `sudo pacman -S python-gobject gtk4 libadwaita clamav`

### Python Dependencies

- Python 3.x
- PyGObject >= 3.48.0
- pycairo >= 1.25.0

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/clamui.git
   cd clamui
   ```

2. **Install system dependencies** (see Requirements above)

3. **Install Python dependencies with uv**:
   ```bash
   uv sync
   ```

4. **Verify ClamAV installation**:
   ```bash
   which clamscan
   clamscan --version
   ```

## Running the Application

```bash
uv run clamui
```

## Project Structure

```
clamui/
├── src/
│   ├── __init__.py
│   ├── main.py              # Application entry point
│   ├── app.py               # Adw.Application class
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── window.py        # Main application window
│   │   └── scan_view.py     # Scan interface component
│   └── core/
│       ├── __init__.py
│       ├── scanner.py       # ClamAV subprocess integration
│       └── utils.py         # Utility functions
├── pyproject.toml
├── uv.lock
├── README.md
└── .gitignore
```

## Usage

1. Launch the application with `uv run clamui`
2. Click the folder selection button to choose a file or directory to scan
3. Click the "Scan" button to start the antivirus scan
4. View the results in the results display area

## ClamAV Exit Codes

The application interprets ClamAV exit codes as follows:
- **0**: No viruses found (clean)
- **1**: Virus(es) found
- **2**: Error occurred during scan

## Development

### Tech Stack

- **Language**: Python 3.x
- **Framework**: PyGObject (GTK4 bindings)
- **UI Toolkit**: GTK4 with libadwaita

### Key Patterns

- Uses `Adw.Application` for modern GNOME application structure
- Background scanning with `threading.Thread` and `GLib.idle_add()` for thread-safe UI updates
- Subprocess integration with `clamscan` for antivirus scanning

### Running Tests

```bash
python -m pytest tests/
```

## License

This project is open source. See LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
