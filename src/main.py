#!/usr/bin/env python3
# ClamUI Entry Point
"""
Main entry point for the ClamUI application.

This module provides the entry point for launching the ClamUI GTK4/Adwaita
desktop application. It handles path setup and initializes the GTK main loop.

Usage:
    python src/main.py
"""

import sys
import os


def _setup_path():
    """
    Ensure the project root is in sys.path.

    This allows the application to be run directly as a script
    (python src/main.py) while still supporting proper package imports.
    """
    # Get the directory containing this file (src/)
    src_dir = os.path.dirname(os.path.abspath(__file__))
    # Get project root (parent of src/)
    project_root = os.path.dirname(src_dir)

    if project_root not in sys.path:
        sys.path.insert(0, project_root)


# Set up path before importing application modules
_setup_path()

from src.app import ClamUIApp


def main():
    """
    Application entry point.

    Creates a ClamUIApp instance and starts the GTK main loop.

    Returns:
        int: Exit code from the application (0 for success).
    """
    app = ClamUIApp()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
