#!/bin/bash
# ClamUI Debian Package Build Script
# Builds a .deb package for ClamUI using dpkg-deb
#
# Usage: ./debian/build-deb.sh [OPTIONS]
#
# Options:
#   --help      Show this help message
#
# Prerequisites: dpkg-deb, fakeroot
# Output: clamui_VERSION_all.deb in the project root

set -e

# Colors for output (only if terminal supports it)
if [ -t 1 ]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    NC='\033[0m' # No Color
else
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    NC=''
fi

# Logging functions
log_info() {
    printf "${BLUE}[INFO]${NC} %s\n" "$1"
}

log_success() {
    printf "${GREEN}[OK]${NC} %s\n" "$1"
}

log_warning() {
    printf "${YELLOW}[WARN]${NC} %s\n" "$1"
}

log_error() {
    printf "${RED}[ERROR]${NC} %s\n" "$1" >&2
}

# Show usage information
show_help() {
    cat << 'EOF'
ClamUI Debian Package Build Script

Usage: ./debian/build-deb.sh [OPTIONS]

Options:
    --help      Show this help message

This script builds a Debian .deb package for ClamUI.

Prerequisites:
    - dpkg-deb (from dpkg-dev package)
    - fakeroot

The script will:
    1. Extract version from pyproject.toml
    2. Create the Debian package directory structure
    3. Copy Python source files (excluding __pycache__)
    4. Create launcher script
    5. Copy desktop entry, icon, and metainfo files
    6. Generate DEBIAN control files
    7. Build the .deb package

Output: clamui_VERSION_all.deb in the project root directory.

Install the generated package with:
    sudo dpkg -i clamui_*.deb
    sudo apt install -f  # if there are missing dependencies
EOF
}

# Parse command line arguments
for arg in "$@"; do
    case "$arg" in
        --help|-h)
            show_help
            exit 0
            ;;
        *)
            log_error "Unknown option: $arg"
            show_help
            exit 1
            ;;
    esac
done

#
# Prerequisites Checking Functions
#

# Check for dpkg-deb availability
check_dpkg_deb() {
    log_info "Checking for dpkg-deb..."

    if command -v dpkg-deb >/dev/null 2>&1; then
        DPKG_VERSION=$(dpkg-deb --version 2>/dev/null | head -n1)
        log_success "dpkg-deb found: $DPKG_VERSION"
        return 0
    fi

    log_error "dpkg-deb not found."
    log_info "Install on Ubuntu/Debian: sudo apt install dpkg-dev"
    return 1
}

# Check for fakeroot availability
check_fakeroot() {
    log_info "Checking for fakeroot..."

    if command -v fakeroot >/dev/null 2>&1; then
        FAKEROOT_VERSION=$(fakeroot --version 2>/dev/null | head -n1)
        log_success "fakeroot found: $FAKEROOT_VERSION"
        return 0
    fi

    log_error "fakeroot not found."
    log_info "Install on Ubuntu/Debian: sudo apt install fakeroot"
    return 1
}

# Check all prerequisites
check_prerequisites() {
    log_info "=== Checking Prerequisites ==="
    echo

    PREREQS_OK=1

    if ! check_dpkg_deb; then
        PREREQS_OK=0
    fi

    if ! check_fakeroot; then
        PREREQS_OK=0
    fi

    echo

    if [ "$PREREQS_OK" = "0" ]; then
        log_error "Missing prerequisites. Please install them and try again."
        log_info "Quick install: sudo apt install dpkg-dev fakeroot"
        exit 1
    fi

    log_success "All prerequisites satisfied!"
    echo
    return 0
}

#
# Main Execution
#

main() {
    echo
    log_info "=== ClamUI Debian Package Builder ==="
    echo

    # Check all prerequisites first
    check_prerequisites

    log_success "Prerequisites check passed. Ready to build package."
    log_info "(Full build functionality will be added in subsequent subtasks)"
}

main "$@"
