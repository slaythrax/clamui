# ClamUI Scanner Types
"""
Type definitions for ClamAV scanner operations.

This module defines the shared data types used by scanner implementations:
- ScanStatus: Enum for scan result states
- ThreatDetail: Dataclass for threat information
- ScanResult: Dataclass for complete scan results
"""

from dataclasses import dataclass
from enum import Enum


class ScanStatus(Enum):
    """Status of a scan operation."""

    CLEAN = "clean"  # No threats found (exit code 0)
    INFECTED = "infected"  # Threats found (exit code 1)
    ERROR = "error"  # Error occurred (exit code 2 or exception)
    CANCELLED = "cancelled"  # Scan was cancelled


@dataclass
class ThreatDetail:
    """Detailed information about a detected threat."""

    file_path: str
    threat_name: str
    category: str
    severity: str


@dataclass
class ScanResult:
    """Result of a scan operation."""

    status: ScanStatus
    path: str
    stdout: str
    stderr: str
    exit_code: int
    infected_files: list[str]
    scanned_files: int
    scanned_dirs: int
    infected_count: int
    error_message: str | None
    threat_details: list[ThreatDetail]

    @property
    def is_clean(self) -> bool:
        """Check if scan found no threats."""
        return self.status == ScanStatus.CLEAN

    @property
    def has_threats(self) -> bool:
        """Check if scan found threats."""
        return self.status == ScanStatus.INFECTED
