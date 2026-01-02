# ClamUI Troubleshooting Guide

This guide helps you diagnose and resolve common issues with ClamUI. If you encounter a problem not covered here, please [open an issue](https://github.com/rooki/clamui/issues) on GitHub.

## Table of Contents

1. [ClamAV Installation Issues](#clamav-installation-issues)
   - [ClamAV not found](#clamav-not-found)
   - [freshclam not installed](#freshclam-not-installed)
   - [clamdscan unavailable](#clamdscan-unavailable)
   - [clamd daemon not running](#clamd-daemon-not-running)
   - [Version compatibility](#version-compatibility)

2. [Flatpak-Specific Issues](#flatpak-specific-issues)
   - [Host ClamAV not accessible](#host-clamav-not-accessible)
   - [Permission denied when scanning files](#permission-denied-when-scanning-files)
   - [Granting additional filesystem access](#granting-additional-filesystem-access)
   - [D-Bus and portal permission issues](#d-bus-and-portal-permission-issues)

3. [System Tray Icon Issues](#system-tray-icon-issues)
   - [Tray icon not appearing](#tray-icon-not-appearing)
   - [AppIndicator library missing](#appindicator-library-missing)
   - [GNOME Shell tray support](#gnome-shell-tray-support)
   - [Desktop environment compatibility](#desktop-environment-compatibility)
   - [Flatpak tray icon issues](#flatpak-tray-icon-issues)
   - [Tray icon status not updating](#tray-icon-status-not-updating)
   - [Tray icon shows wrong icon or generic fallback](#tray-icon-shows-wrong-icon-or-generic-fallback)

4. [File Manager Context Menu Issues](#file-manager-context-menu-issues)
   - [Context menu not appearing](#context-menu-not-appearing)
   - [Desktop file permissions](#desktop-file-permissions)
   - [Manual context menu installation](#manual-context-menu-installation)
   - [File manager refresh requirements](#file-manager-refresh-requirements)

5. [Scanning Errors](#scanning-errors)
   - [Permission denied errors](#permission-denied-errors)
   - [Path validation failures](#path-validation-failures)
   - [Symlink security warnings](#symlink-security-warnings)
   - [Daemon connection failures](#daemon-connection-failures)
   - [Scan timeout issues](#scan-timeout-issues)

6. [Database Update Issues](#database-update-issues)
   - [freshclam permission errors](#freshclam-permission-errors)
   - [Running updates without root](#running-updates-without-root)
   - [Database location issues](#database-location-issues)
   - [Network connectivity problems](#network-connectivity-problems)
   - [Outdated database warnings](#outdated-database-warnings)

7. [Scheduled Scanning Issues](#scheduled-scanning-issues)
   - [Systemd user timers not working](#systemd-user-timers-not-working)
   - [Cron fallback configuration](#cron-fallback-configuration)
   - [Battery detection issues](#battery-detection-issues)
   - [Scheduled scans not running](#scheduled-scans-not-running)
   - [Verifying scheduled scan logs](#verifying-scheduled-scan-logs)

8. [General Issues](#general-issues)
   - [Application won't start](#application-wont-start)
   - [UI appears frozen](#ui-appears-frozen)
   - [High CPU or memory usage](#high-cpu-or-memory-usage)
   - [Quarantine operations failing](#quarantine-operations-failing)
   - [Settings not persisting](#settings-not-persisting)

9. [Frequently Asked Questions (FAQ)](#frequently-asked-questions-faq)
   - [What is ClamUI vs ClamAV?](#what-is-clamui-vs-clamav)
   - [Why is scanning slow?](#why-is-scanning-slow)
   - [How do I enable daemon mode?](#how-do-i-enable-daemon-mode)
   - [What does quarantine do?](#what-does-quarantine-do)
   - [How do I create custom scan profiles?](#how-do-i-create-custom-scan-profiles)
   - [What are the system requirements?](#what-are-the-system-requirements)

10. [Getting Help](#getting-help)

---

## ClamAV Installation Issues

### ClamAV not found

**Symptoms**: Error message "ClamAV is not installed" or "clamscan command not found"

**Solution**: Install ClamAV on your system

```bash
# Ubuntu/Debian
sudo apt install clamav

# Fedora
sudo dnf install clamav clamav-update

# Arch Linux
sudo pacman -S clamav
```

Verify the installation:

```bash
clamscan --version
```

### freshclam not installed

**Symptoms**: Database update fails with "freshclam not found"

**Solution**: Install the freshclam package (usually included with ClamAV)

```bash
# Ubuntu/Debian
sudo apt install clamav-freshclam

# Fedora (included in clamav-update)
sudo dnf install clamav-update

# Arch Linux (included in clamav)
sudo pacman -S clamav
```

### clamdscan unavailable

**Symptoms**: Warning about daemon scanner not available

**Solution**: Install and start the ClamAV daemon

```bash
# Ubuntu/Debian
sudo apt install clamav-daemon
sudo systemctl enable --now clamav-daemon

# Fedora
sudo dnf install clamd
sudo systemctl enable --now clamd@scan

# Arch Linux
sudo pacman -S clamav
sudo systemctl enable --now clamd
```

### clamd daemon not running

**Symptoms**: "Daemon connection failed" errors

**Solution**: Start the ClamAV daemon

```bash
# Check daemon status
sudo systemctl status clamav-daemon  # Ubuntu/Debian
sudo systemctl status clamd@scan     # Fedora
sudo systemctl status clamd          # Arch

# Start the daemon
sudo systemctl start clamav-daemon   # Ubuntu/Debian
sudo systemctl start clamd@scan      # Fedora
sudo systemctl start clamd           # Arch
```

### Version compatibility

**Symptoms**: Unexpected behavior or parsing errors

**Solution**: Ensure you're using a supported ClamAV version (0.103+)

```bash
clamscan --version
```

If your version is too old, update ClamAV:

```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade clamav

# Fedora
sudo dnf upgrade clamav

# Arch Linux
sudo pacman -Syu clamav
```

---

## Flatpak-Specific Issues

### Host ClamAV not accessible

**Symptoms**:
- Error message "ClamAV is not installed"
- Error message "clamscan command not found"
- ClamUI can't detect ClamAV despite it being installed

**Cause**: ClamUI Flatpak runs in a sandbox and needs ClamAV installed on the **host system** (not inside Flatpak)

**Solution**: Install ClamAV on your host OS (outside Flatpak)

```bash
# Install on your host OS (outside Flatpak)
sudo apt install clamav  # Ubuntu/Debian
sudo dnf install clamav  # Fedora
sudo pacman -S clamav    # Arch
```

**How it works**: ClamUI uses `flatpak-spawn --host` to access host ClamAV binaries. This allows the sandboxed Flatpak app to use the ClamAV installation on your host system.

**Verify it works**:
```bash
# Test that ClamAV is accessible from the host
flatpak run --command=sh com.github.rooki.ClamUI -c "flatpak-spawn --host clamscan --version"
```

### Permission denied when scanning files

**Symptoms**:
- "Permission denied" when scanning directories
- "Cannot read" error messages
- Files/folders not appearing in scan results
- Quarantine operations fail

**Cause**: Flatpak sandbox restricts filesystem access by default

**Solution**: Grant Flatpak access to the directories you want to scan

```bash
# Grant read-only access to a specific directory
flatpak override --user --filesystem=/path/to/directory:ro com.github.rooki.ClamUI

# Grant full access (needed for quarantine operations)
flatpak override --user --filesystem=/path/to/directory com.github.rooki.ClamUI
```

**Common directories to grant access**:

```bash
# Home directory (usually already granted)
flatpak override --user --filesystem=home com.github.rooki.ClamUI

# External drives and USB devices
flatpak override --user --filesystem=/media com.github.rooki.ClamUI
flatpak override --user --filesystem=/mnt com.github.rooki.ClamUI
flatpak override --user --filesystem=/run/media com.github.rooki.ClamUI

# Additional common locations
flatpak override --user --filesystem=/var com.github.rooki.ClamUI  # For system scans
flatpak override --user --filesystem=/opt com.github.rooki.ClamUI  # For installed apps
```

**Note**: Read-only access (`:ro`) is sufficient for scanning, but quarantine operations require full write access.

### Granting additional filesystem access

**Symptoms**: Can't scan files outside of allowed directories

**Solution**: View and modify Flatpak permissions

**Command line method**:

```bash
# View current permissions
flatpak info --show-permissions com.github.rooki.ClamUI

# Grant access to a specific directory
flatpak override --user --filesystem=/path/to/directory com.github.rooki.ClamUI

# Grant access to all files (use with caution - reduces sandbox security)
flatpak override --user --filesystem=host com.github.rooki.ClamUI

# Remove a specific permission
flatpak override --user --nofilesystem=/path/to/directory com.github.rooki.ClamUI

# Reset permissions to default
flatpak override --user --reset com.github.rooki.ClamUI
```

**GUI method (Flatseal)**:

For easier permission management, install Flatseal:

```bash
flatpak install flathub com.github.tchx84.Flatseal
```

Then use Flatseal to:
1. Find "ClamUI" in the application list
2. Scroll to "Filesystem" section
3. Toggle access for specific directories
4. Click the "+" button to add custom paths

### D-Bus and portal permission issues

**Symptoms**:
- Notifications not appearing
- File picker dialogs not working
- "Open with file manager" button doesn't work
- Desktop integration features fail

**Cause**: Missing D-Bus or portal permissions

**Solution 1**: Ensure D-Bus permissions are set

```bash
# Verify D-Bus access
flatpak info --show-permissions com.github.rooki.ClamUI | grep -E 'talk-name|system-talk-name'

# Expected permissions should include:
# - org.freedesktop.Notifications (for notifications)
# - org.freedesktop.portal.* (for file picker and desktop integration)
```

**Solution 2**: Fix missing permissions

If D-Bus permissions are missing, reinstall the Flatpak:

```bash
flatpak uninstall com.github.rooki.ClamUI
flatpak install flathub com.github.rooki.ClamUI
```

**Solution 3**: Grant portal access manually (if needed)

```bash
# Grant portal access
flatpak override --user --talk-name=org.freedesktop.Notifications com.github.rooki.ClamUI
flatpak override --user --talk-name=org.freedesktop.portal.Desktop com.github.rooki.ClamUI
flatpak override --user --talk-name=org.freedesktop.portal.FileChooser com.github.rooki.ClamUI
```

**Troubleshooting notifications**:

If notifications still don't work:

1. Check that your desktop environment supports notifications
2. Verify notification daemon is running:
   ```bash
   ps aux | grep notification
   ```
3. Test notifications from the Flatpak:
   ```bash
   flatpak run --command=sh com.github.rooki.ClamUI -c \
     "notify-send 'Test' 'This is a test notification'"
   ```

---

## System Tray Icon Issues

### Tray icon not appearing

**Symptoms**: ClamUI runs but no tray icon is visible in the system tray

**Possible causes and solutions**:

1. **AppIndicator library missing** - See [AppIndicator library missing](#appindicator-library-missing)
2. **GNOME Shell missing extension** - See [GNOME Shell tray support](#gnome-shell-tray-support)
3. **Desktop environment doesn't support tray** - See [Desktop environment compatibility](#desktop-environment-compatibility)
4. **Tray disabled in settings** - Open ClamUI Preferences → General and enable "Show tray icon"
5. **Flatpak-specific issues** - See [Flatpak tray icon issues](#flatpak-tray-icon-issues)

**Quick diagnostic**:

```bash
# Check if AppIndicator library is installed
dpkg -l | grep ayatana  # Ubuntu/Debian
rpm -qa | grep ayatana  # Fedora

# Run ClamUI from terminal to see error messages
clamui  # or: flatpak run com.github.rooki.ClamUI
```

Look for error messages like:
- `"System tray indicator unavailable: Missing library"`
- `"AppIndicator library not found"`
- `"GTK version conflict"`

### AppIndicator library missing

**Symptoms**:
- Warning in logs: `"AppIndicator library not found"`
- Error message: `"Missing library: No module named 'gi.repository.AyatanaAppIndicator3'"`
- Tray icon doesn't appear on any desktop environment

**Cause**: The AyatanaAppIndicator3 library is not installed on your system

**Solution**: Install the AyatanaAppIndicator library

```bash
# Ubuntu/Debian
sudo apt install gir1.2-ayatanaappindicator3-0.1

# Fedora
sudo dnf install libayatana-appindicator-gtk3

# Arch Linux
sudo pacman -S libayatana-appindicator

# openSUSE
sudo zypper install typelib-1_0-AyatanaAppIndicator3-0_1
```

**Verify installation**:

```bash
# Check if library is available
python3 -c "from gi.repository import AyatanaAppIndicator3; print('AppIndicator available')"
```

**After installation**: Restart ClamUI for changes to take effect.

### GNOME Shell tray support

**Symptoms**:
- AppIndicator library installed but tray icon still not visible on GNOME
- Works on other desktop environments (KDE, XFCE) but not GNOME
- GNOME Shell version 3.38+ or GNOME 40+

**Cause**: GNOME Shell removed native tray icon support and requires an extension

**Solution**: Install the AppIndicator Support extension

**Method 1: Via GNOME Extensions website** (recommended)

1. Visit [GNOME Extensions: AppIndicator Support](https://extensions.gnome.org/extension/615/appindicator-support/)
2. Click the ON/OFF toggle to install
3. If prompted, install the browser extension first
4. Enable the extension in GNOME Extensions app
5. Restart ClamUI

**Method 2: Via package manager**

```bash
# Ubuntu/Debian
sudo apt install gnome-shell-extension-appindicator

# Fedora
sudo dnf install gnome-shell-extension-appindicator

# After installation, enable the extension
gnome-extensions enable appindicatorsupport@rgcjonas.gmail.com
```

**Method 3: Via Extension Manager app**

1. Install Extension Manager: `flatpak install flathub com.mattjakeman.ExtensionManager`
2. Search for "AppIndicator and KStatusNotifierItem Support"
3. Install and enable
4. Restart GNOME Shell: Press `Alt+F2`, type `r`, press Enter

**Verify extension is active**:

```bash
gnome-extensions list --enabled | grep appindicator
```

### Desktop environment compatibility

**Symptoms**: Tray icon works on some desktop environments but not others

**Desktop-specific solutions**:

**KDE Plasma**:
- Tray icons should work natively with AppIndicator installed
- If icon doesn't appear, right-click the system tray area → Configure System Tray → Entries → Enable "ClamUI"

**XFCE**:
- Install the XFCE Panel Plugin: `sudo apt install xfce4-indicator-plugin`
- Add "Indicator Plugin" to your panel: Right-click panel → Panel → Add New Items → Indicator Plugin
- Restart ClamUI

**Cinnamon**:
- Tray icons should work natively with AppIndicator installed
- If icon doesn't appear, ensure "System Tray" applet is added to your panel
- Applets → System Tray → Enable

**MATE**:
- Install indicator support: `sudo apt install mate-indicator-applet`
- Add to panel: Right-click panel → Add to Panel → Indicator Applet
- Restart ClamUI

**LXQt**:
- Install StatusNotifier plugin: `sudo apt install lxqt-panel-plugin-statusnotifier`
- Add to panel: Right-click panel → Manage Widgets → StatusNotifier

**Budgie**:
- Tray icons should work natively with AppIndicator installed
- Check Budgie Settings → Raven → Show System Tray

### Flatpak tray icon issues

**Symptoms**:
- Tray icon doesn't appear when using Flatpak version
- Works with native installation but not Flatpak
- Error: `"Failed to start tray service subprocess"`

**Cause**: Flatpak sandbox restrictions or missing host libraries

**Solution 1: Install AppIndicator on host system**

The Flatpak version requires AppIndicator library on the **host system** (not inside Flatpak):

```bash
# Install on your host OS (outside Flatpak)
sudo apt install gir1.2-ayatanaappindicator3-0.1  # Ubuntu/Debian
sudo dnf install libayatana-appindicator-gtk3     # Fedora
sudo pacman -S libayatana-appindicator             # Arch
```

**Solution 2: Grant D-Bus permissions**

Ensure the Flatpak has tray icon permissions:

```bash
# View current permissions
flatpak info --show-permissions com.github.rooki.ClamUI

# Grant StatusNotifier permissions (if missing)
flatpak override --user --talk-name=org.kde.StatusNotifierWatcher com.github.rooki.ClamUI
```

**Solution 3: Enable XDG Desktop Portal**

Some desktop environments need the desktop portal for tray support:

```bash
# Install the portal for your desktop environment
sudo apt install xdg-desktop-portal-gtk   # GNOME/GTK-based
sudo apt install xdg-desktop-portal-kde   # KDE
```

**Verify tray service is running**:

```bash
# Check if tray subprocess starts
flatpak run com.github.rooki.ClamUI
# Look for messages like: "Starting tray service" or "Tray service is ready"
```

### Tray icon status not updating

**Symptoms**:
- Tray icon appears but doesn't change color/icon during scans
- Icon stuck on one status (protected, scanning, etc.)
- Progress percentage not showing during scans

**Possible causes and solutions**:

**Cause 1: Icon theme doesn't have required symbolic icons**

```bash
# Test if theme has required icons
gtk-update-icon-cache -f /usr/share/icons/YOUR_THEME_NAME/

# Switch to a standard icon theme temporarily
gsettings set org.gnome.desktop.interface icon-theme 'Adwaita'
```

**Cause 2: Tray service subprocess crashed**

```bash
# Check for errors in logs
journalctl --user -u clamui --since today | grep -i tray

# Look for:
# - "Tray service subprocess started"
# - "Tray service is ready"
# - Any error messages
```

**Cause 3: Communication issue between main app and tray subprocess**

```bash
# Run with debug logging
CLAMUI_DEBUG=1 clamui

# Or for Flatpak:
flatpak run --env=CLAMUI_DEBUG=1 com.github.rooki.ClamUI
```

**Solution**: Try these steps in order:

1. **Restart ClamUI** - Kills and restarts the tray subprocess
2. **Disable and re-enable tray icon**:
   - Open ClamUI Preferences → General
   - Uncheck "Show tray icon"
   - Click Apply
   - Check "Show tray icon" again
3. **Clear cached icon theme**:
   ```bash
   rm -rf ~/.cache/icon-cache
   gtk-update-icon-cache
   ```
4. **Check for multiple instances**:
   ```bash
   # Kill any existing ClamUI processes
   pkill -9 clamui
   # Start fresh
   clamui
   ```

### Tray icon shows wrong icon or generic fallback

**Symptoms**:
- Tray icon shows generic icons instead of ClamUI-specific icons
- All statuses show the same icon
- Icon doesn't match the application state

**Cause**: Icon theme missing symbolic icons or ClamUI icon not installed

**Solution**:

```bash
# Install complete icon theme
sudo apt install adwaita-icon-theme-full

# Update icon cache
sudo gtk-update-icon-cache -f /usr/share/icons/Adwaita/
sudo gtk-update-icon-cache -f /usr/share/icons/hicolor/

# For user-installed icons
gtk-update-icon-cache ~/.local/share/icons/hicolor/
```

**Verify ClamUI icon is installed**:

```bash
# Check for ClamUI icon
ls -la /usr/share/icons/hicolor/scalable/apps/com.github.rooki.clamui.*
ls -la ~/.local/share/icons/hicolor/scalable/apps/com.github.rooki.clamui.*
```

---

## File Manager Context Menu Issues

### Context menu not appearing

**Symptoms**: "Scan with ClamUI" option missing in right-click menu

**Solution**: Varies by file manager

**Nautilus (GNOME Files)**:
```bash
# Ensure desktop file exists
ls ~/.local/share/applications/com.github.rooki.ClamUI.desktop

# Update desktop database
update-desktop-database ~/.local/share/applications

# Restart Nautilus
nautilus -q
```

**Dolphin (KDE)**:
```bash
# Same as Nautilus
update-desktop-database ~/.local/share/applications
killall dolphin
```

**Nemo (Cinnamon)**:
```bash
# Check Nemo action file
ls ~/.local/share/nemo/actions/com.github.rooki.ClamUI.nemo_action

# Restart Nemo
nemo -q
```

### Desktop file permissions

**Symptoms**: Desktop file exists but context menu doesn't work

**Solution**: Ensure the desktop file is executable

```bash
chmod +x ~/.local/share/applications/com.github.rooki.ClamUI.desktop
```

### Manual context menu installation

**Symptoms**: Flatpak installation didn't set up context menu

**Solution**: Manually export the desktop file

```bash
# For Flatpak installations
flatpak run --command=sh com.github.rooki.ClamUI -c \
  "cp /app/share/applications/com.github.rooki.ClamUI.desktop ~/.local/share/applications/"

update-desktop-database ~/.local/share/applications
```

### File manager refresh requirements

**Symptoms**: Context menu appears but doesn't work correctly

**Solution**: Completely restart your desktop session

```bash
# Log out and log back in, or restart file manager
nautilus -q && nautilus &  # GNOME
killall dolphin && dolphin &  # KDE
nemo -q && nemo &  # Cinnamon
```

---

## Scanning Errors

### Permission denied errors

**Symptoms**: "Permission denied" when scanning files or directories

**Solutions**:

1. **Check file permissions**:
   ```bash
   ls -la /path/to/file
   ```

2. **For Flatpak**: Grant filesystem access (see [Flatpak-Specific Issues](#flatpak-specific-issues))

3. **For system files**: Some system directories require root access:
   ```bash
   # Run with elevated permissions (use with caution)
   sudo -E clamui
   ```

### Path validation failures

**Symptoms**: "Invalid path" errors

**Solution**: Ensure paths are:
- Absolute (start with `/`)
- Don't contain null bytes or newlines
- Actually exist on the filesystem

```bash
# Verify path exists
ls -la /path/to/scan
```

### Symlink security warnings

**Symptoms**: Warnings about symbolic links during scans

**Solution**: This is expected behavior for security. ClamUI validates symlinks to prevent:
- Directory traversal attacks
- Scanning the same file multiple times

To scan symlink targets, scan the actual target directory instead.

### Daemon connection failures

**Symptoms**: "Failed to connect to clamd" errors

**Solution**: Check daemon status and socket path

```bash
# Verify daemon is running
sudo systemctl status clamav-daemon

# Check socket exists
ls -la /var/run/clamav/clamd.ctl  # Debian/Ubuntu
ls -la /var/run/clamd.scan/clamd.sock  # Fedora

# Switch to clamscan backend in ClamUI preferences
# Settings → Scan Backend → "Direct scan (clamscan)"
```

### Scan timeout issues

**Symptoms**: Scans fail with timeout errors on large files

**Solution**: Increase timeout or use daemon mode

1. **Enable daemon mode** (faster for large files):
   - Open ClamUI preferences
   - Set Scan Backend to "Daemon (clamdscan)" or "Auto"

2. **For very large files**, configure clamd timeout:
   ```bash
   # Edit /etc/clamav/clamd.conf
   sudo nano /etc/clamav/clamd.conf

   # Increase timeout (in milliseconds)
   ReadTimeout 300000

   # Restart daemon
   sudo systemctl restart clamav-daemon
   ```

---

## Database Update Issues

### freshclam permission errors

**Symptoms**: "Permission denied" when updating virus database

**Solution**: Run freshclam with appropriate permissions

```bash
# Option 1: Use sudo
sudo freshclam

# Option 2: Configure freshclam to run as your user (advanced)
# Edit /etc/clamav/freshclam.conf
sudo nano /etc/clamav/freshclam.conf
# Set: DatabaseOwner yourusername
```

### Running updates without root

**Symptoms**: Don't have root access but need to update database

**Solution**: Use local database directory

```bash
# Create local database directory
mkdir -p ~/.local/share/clamav

# Update to local directory
freshclam --datadir=$HOME/.local/share/clamav

# Configure ClamUI to use local database (if needed)
# This is usually automatic
```

### Database location issues

**Symptoms**: ClamAV can't find virus database

**Solution**: Verify database location and permissions

```bash
# Common database locations
ls -la /var/lib/clamav/  # Most distributions
ls -la /var/db/clamav/   # Some systems

# Update database
sudo freshclam
```

### Network connectivity problems

**Symptoms**: Database update fails with network errors

**Solution**: Check network and DNS

```bash
# Test connectivity to ClamAV mirrors
ping database.clamav.net

# Update with verbose output
sudo freshclam -v

# Try different mirror (in /etc/clamav/freshclam.conf)
sudo nano /etc/clamav/freshclam.conf
# Add: DatabaseMirror db.us.clamav.net
```

### Outdated database warnings

**Symptoms**: Warning that virus database is outdated

**Solution**: Update the database regularly

```bash
# Manual update
sudo freshclam

# Enable automatic updates (recommended)
sudo systemctl enable --now clamav-freshclam  # Ubuntu/Debian
sudo systemctl enable --now clamav-freshclam.service  # Fedora

# Verify automatic updates are running
sudo systemctl status clamav-freshclam
```

---

## Scheduled Scanning Issues

### Systemd user timers not working

**Symptoms**: Scheduled scans don't run automatically

**Solution**: Check systemd timer status

```bash
# List user timers
systemctl --user list-timers

# Check specific timer
systemctl --user status clamui-scan-*.timer

# View timer logs
journalctl --user -u clamui-scan-*.timer

# Enable linger for scans to run when logged out
loginctl enable-linger $USER
```

### Cron fallback configuration

**Symptoms**: Systemd not available, need cron-based scheduling

**Solution**: Manually configure cron

```bash
# Edit crontab
crontab -e

# Add scheduled scan (example: daily at 2 AM)
0 2 * * * /usr/bin/clamui-scheduled-scan --profile "Full Scan"

# Verify cron entry
crontab -l
```

### Battery detection issues

**Symptoms**: Scans run on battery when configured not to

**Solution**: Check battery detection

```bash
# Verify battery status detection
cat /sys/class/power_supply/BAT*/status

# Check ClamUI battery settings
# Preferences → Scheduled Scans → "Skip scans on battery"
```

### Scheduled scans not running

**Symptoms**: Timer/cron configured but scans don't execute

**Solution**: Debug scheduled scan execution

```bash
# Test manual execution
clamui-scheduled-scan --profile "Quick Scan"

# Check logs
journalctl --user -u clamui-scan-* --since today

# Verify scan profile exists
clamui  # Open app and check Profiles
```

### Verifying scheduled scan logs

**Symptoms**: Want to confirm scans are running

**Solution**: Check scan history

```bash
# View ClamUI scan logs
ls -lh ~/.local/share/clamui/logs/

# View recent log file
cat ~/.local/share/clamui/logs/scan_$(date +%Y%m%d).json

# Check systemd logs
journalctl --user -u clamui-scan-* --since "1 week ago"
```

---

## General Issues

### Application won't start

**Symptoms**: ClamUI fails to launch or crashes immediately

**Solution**: Check dependencies and logs

```bash
# Verify GTK4 and Adwaita are installed
dpkg -l | grep gtk-4  # Ubuntu/Debian
rpm -qa | grep gtk4   # Fedora

sudo apt install gir1.2-gtk-4.0 gir1.2-adw-1  # Ubuntu/Debian
sudo dnf install gtk4 libadwaita  # Fedora

# Run from terminal to see error messages
clamui

# For Flatpak
flatpak run com.github.rooki.ClamUI
```

### UI appears frozen

**Symptoms**: Interface becomes unresponsive

**Solution**: This usually indicates a background operation

1. **During scans**: Large directory scans can take time. Check the progress indicator.
2. **Force quit if necessary**:
   ```bash
   pkill -9 clamui
   ```
3. **Report the issue**: If reproducible, [open an issue](https://github.com/rooki/clamui/issues)

### High CPU or memory usage

**Symptoms**: ClamUI or ClamAV consuming excessive resources

**Solution**: Optimize scan settings

1. **Use daemon mode** for better performance:
   - Preferences → Scan Backend → "Daemon (clamdscan)"

2. **Reduce scan scope**:
   - Use scan profiles to exclude large directories
   - Skip already-scanned files

3. **Limit ClamAV resources**:
   ```bash
   # Edit /etc/clamav/clamd.conf
   sudo nano /etc/clamav/clamd.conf

   # Reduce thread count
   MaxThreads 2

   sudo systemctl restart clamav-daemon
   ```

### Quarantine operations failing

**Symptoms**: Can't quarantine or restore files

**Solution**: Check quarantine directory permissions

```bash
# Verify quarantine directory exists
ls -la ~/.local/share/clamui/quarantine/

# Create if missing
mkdir -p ~/.local/share/clamui/quarantine/

# Check permissions
chmod 700 ~/.local/share/clamui/quarantine/

# Check database
ls -la ~/.local/share/clamui/quarantine.db
```

### Settings not persisting

**Symptoms**: Preferences reset after restarting ClamUI

**Solution**: Check settings file permissions

```bash
# Verify settings directory
ls -la ~/.config/clamui/

# Create if missing
mkdir -p ~/.config/clamui/

# Check settings file
cat ~/.config/clamui/settings.json

# Reset to defaults if corrupted
rm ~/.config/clamui/settings.json
```

---

## Frequently Asked Questions (FAQ)

### What is ClamUI vs ClamAV?

**ClamAV** is the open-source antivirus engine that runs from the command line. **ClamUI** is a graphical user interface (GUI) that makes ClamAV easier to use by providing:

- Point-and-click file selection
- Visual scan results
- Quarantine management
- Scheduled scanning
- Integration with file managers

**ClamUI requires ClamAV to be installed** to function.

### Why is scanning slow?

Scanning speed depends on several factors:

1. **Scan backend**: Daemon mode (`clamdscan`) is faster than direct mode (`clamscan`)
   - Solution: Enable daemon in ClamUI preferences

2. **File size and count**: Large files or directories with many files take longer
   - Solution: Use scan profiles to limit scope

3. **System resources**: CPU, disk speed, and available RAM affect performance
   - Solution: Close other applications during scans

4. **Database loading**: `clamscan` loads the virus database for each scan
   - Solution: Use daemon mode which keeps the database in memory

### How do I enable daemon mode?

Daemon mode provides faster scanning by keeping ClamAV in memory:

1. **Install the daemon**:
   ```bash
   sudo apt install clamav-daemon  # Ubuntu/Debian
   sudo dnf install clamd  # Fedora
   ```

2. **Start the daemon**:
   ```bash
   sudo systemctl enable --now clamav-daemon  # Ubuntu/Debian
   sudo systemctl enable --now clamd@scan  # Fedora
   ```

3. **Configure ClamUI**:
   - Open Preferences
   - Set Scan Backend to "Daemon (clamdscan)" or "Auto"

### What does quarantine do?

Quarantine **isolates potentially harmful files** to prevent them from causing damage:

- **Secure storage**: Files are moved to `~/.local/share/clamui/quarantine/`
- **Metadata tracking**: Original location, hash, and detection info stored in database
- **Safe restoration**: Files can be restored to their original location if needed
- **Permanent deletion**: Quarantined files can be deleted permanently

**Important**: Quarantined files cannot execute or cause harm while in quarantine.

### How do I create custom scan profiles?

Scan profiles let you save scan configurations for different use cases:

1. **Open ClamUI**
2. **Navigate to Profiles** in the sidebar
3. **Click "New Profile"**
4. **Configure**:
   - Name your profile
   - Select target paths to scan
   - Add exclusion patterns (optional)
   - Set scan options
5. **Click "Save"**

**Example profiles**:
- **Quick Scan**: `~/Downloads`, `~/Desktop`
- **Full Scan**: `/home`
- **Custom**: Specific project directories

### What are the system requirements?

**Minimum requirements**:
- **OS**: Linux (any distribution)
- **Python**: 3.10 or higher
- **GTK**: GTK4
- **Adwaita**: libadwaita 1.0+
- **ClamAV**: 0.103 or higher
- **RAM**: 512 MB (2 GB recommended)
- **Disk**: 500 MB for ClamAV database

**Optional**:
- **Tray icon**: AyatanaAppIndicator3 library
- **GNOME**: AppIndicator Support extension
- **Daemon mode**: clamav-daemon package

---

## Getting Help

If you've tried the solutions in this guide and still need help:

### Community Support

1. **GitHub Issues**: [Report a bug or request a feature](https://github.com/rooki/clamui/issues)
2. **Discussions**: [Ask questions and share tips](https://github.com/rooki/clamui/discussions)

### Before Reporting an Issue

Please include:

1. **ClamUI version**: `clamui --version` or check About dialog
2. **Installation method**: Flatpak, .deb, or source
3. **Linux distribution and version**: `lsb_release -a`
4. **ClamAV version**: `clamscan --version`
5. **Error messages**: Copy exact error text or screenshots
6. **Steps to reproduce**: What you did before the error occurred

### Useful Debug Commands

```bash
# Check ClamUI version
clamui --version

# Check ClamAV version
clamscan --version

# Test ClamAV directly
clamscan --version && echo "ClamAV is working"

# Check GTK version
pkg-config --modversion gtk4

# View application logs
journalctl --user -u clamui --since today

# For Flatpak
flatpak run com.github.rooki.ClamUI --verbose
```

---

## See Also

- [README.md](../README.md) - Project overview and features
- [INSTALL.md](./INSTALL.md) - Installation instructions for all platforms
- [DEVELOPMENT.md](./DEVELOPMENT.md) - Development setup and contributing guidelines
- [ClamAV Documentation](https://docs.clamav.net/) - Official ClamAV documentation
- [GTK4 Documentation](https://docs.gtk.org/gtk4/) - GTK4 API reference
