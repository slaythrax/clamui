<div align="center">

<img src="https://raw.githubusercontent.com/linx-systems/clamui/master/icons/io.github.linx_systems.ClamUI.svg" alt="ClamUI Logo" width="140" height="140">

# ClamUI

<p align="center">
  <strong>A modern Linux desktop application for ClamAV antivirus</strong>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License"></a>
  <a href="#"><img src="https://img.shields.io/badge/platform-Linux-lightgrey.svg" alt="Platform"></a>
  <a href="https://flathub.org/en/apps/io.github.linx_systems.ClamUI"><img src="https://flathub.org/api/badge?locale=en" alt="Get ClamUI on Flathub"></a>
</p>

<p align="center">
  Built with <strong>PyGObject</strong>, <strong>GTK4</strong>, and <strong>Adwaita</strong> for a native GNOME appearance
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#screenshots">Screenshots</a> •
  <a href="#quick-start">Installation</a> •
  <a href="#documentation">Documentation</a>
</p>

<br>

<img src="./screenshots/main_view.png" alt="Main View" width="800">

</div>

<br>

---

## Features

<table>
<tr>
<td width="50%">

### Scanning & Protection
- **Easy File Scanning** - Native GTK4 file dialogs
- **Async Scanning** - Background processing keeps UI responsive
- **Quarantine Management** - Safely isolate detected threats
- **Scan Profiles** - Custom configurations for different scenarios

</td>
<td width="50%">

### Management & Integration
- **Scan History** - Track and review past results
- **Statistics Dashboard** - Monitor activity and detections
- **VirusTotal Integration** - Optional enhanced threat analysis
- **File Manager Integration** - Right-click scanning in Nautilus, Dolphin, Nemo

</td>
</tr>
<tr>
<td width="50%">

### User Experience
- **Modern UI** - Native Adwaita styling with GNOME integration
- **System Tray** - Quick actions and scan progress
- **Desktop Notifications** - Stay informed of scan results

</td>
<td width="50%">

### Flexibility
- **Multiple Scan Backends** - Daemon (clamd) or direct (clamscan)
- **Scheduled Scans** - Automatic scanning with systemd/cron
- **Customizable Settings** - Extensive configuration options

</td>
</tr>
</table>

---

## Screenshots

<div align="center">

| Scan Results | Quarantine Management |
|:------------:|:---------------------:|
| ![Scan Results](./screenshots/main_view_with_scan_result.png) | ![Quarantine View](./screenshots/quarantine_view.png) |

| ClamAV Components Status | Scan History |
|:------------------------:|:------------:|
| ![Components View](./screenshots/components_view.png) | ![History View](./screenshots/history_view.png) |

| Scan Profiles | Settings |
|:-------------:|:--------:|
| ![Profile Management](./screenshots/profile_management.png) | ![Config View](./screenshots/config_view.png) |

</div>

---

## Quick Start

### Flatpak (Recommended)

```bash
flatpak install flathub io.github.linx_systems.ClamUI
flatpak run io.github.linx_systems.ClamUI
```

### From Source

```bash
git clone https://github.com/linx-systems/clamui.git
cd clamui
uv sync
uv run clamui
```

> **More Installation Options:** See the [Installation Guide](./docs/INSTALL.md) for .deb packages and system-wide installation

---

## Usage

### GUI Application

1. Launch ClamUI from your application menu or terminal
2. Select a file or folder to scan
3. Click "Scan" to start the antivirus scan
4. View results and take action on any threats detected

### Command Line

```bash
# Launch the application
clamui

# Scan specific files directly
clamui /path/to/file1 /path/to/folder
```

> **Detailed Instructions:** See the [User Guide](./docs/USER_GUIDE.md)

---

## Configuration

**Configuration Location:** `~/.config/clamui/settings.json`

### Key Configuration Options

| Category | Options |
|----------|---------|
| **Scan Backend** | Automatic detection, daemon (clamd), or direct clamscan |
| **Notifications** | Desktop notifications for scan results and updates |
| **Auto-Quarantine** | Automatically quarantine detected threats |
| **Scheduled Scans** | Configure automatic scanning with systemd or cron |
| **System Tray** | Enable start minimized and minimize to tray options |
| **Scan Profiles** | Create custom scan configurations with exclusion patterns |

> **Full Reference:** See the [Configuration Reference](./docs/CONFIGURATION.md) for all 15 settings and examples

---

## Documentation

| Document | Description |
|----------|-------------|
| **[User Guide](./docs/USER_GUIDE.md)** | Complete guide to using ClamUI features |
| **[Installation Guide](./docs/INSTALL.md)** | Flatpak, .deb, context menu, and tray setup |
| **[Troubleshooting Guide](./docs/TROUBLESHOOTING.md)** | Common issues and solutions |
| **[Development Guide](./docs/DEVELOPMENT.md)** | Dev environment, testing, and contributing |
| **[Scan Backend Guide](./docs/SCAN_BACKENDS.md)** | Backend options, performance comparison, and selection guide |
| **[Security Policy](./SECURITY.txt)** | Security contact and reporting |

---

## Requirements

| Component | Description |
|-----------|-------------|
| **ClamAV** | The `clamscan` command-line tool must be installed |
| **GTK4 + libadwaita** | For the graphical interface |
| **Python 3.x** | With PyGObject bindings |

> **Platform-Specific Instructions:** See the [Installation Guide](./docs/INSTALL.md) for dependency installation

---

## Contributing

Contributions are welcome! Check out the [Development Guide](./docs/DEVELOPMENT.md) for:

- Setting up the development environment
- Running tests with coverage
- Code style guidelines
- Submitting pull requests

---

## License

This project is open source. See [LICENSE](LICENSE) file for details.

---

<div align="center">

**Made with care for the Linux community**

[Star on GitHub](https://github.com/linx-systems/clamui) • [Report Bug](https://github.com/linx-systems/clamui/issues) • [Request Feature](https://github.com/linx-systems/clamui/issues)

</div>
