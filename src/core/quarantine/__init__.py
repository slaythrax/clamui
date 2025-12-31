# ClamUI Quarantine Module
"""
Quarantine management module for ClamUI providing secure threat isolation.
Handles moving detected threats to quarantine, metadata persistence, and restoration.
"""

from .database import QuarantineDatabase, QuarantineEntry
from .file_handler import (
    FileOperationResult,
    FileOperationStatus,
    SecureFileHandler,
)

__all__ = [
    "QuarantineDatabase",
    "QuarantineEntry",
    "FileOperationResult",
    "FileOperationStatus",
    "SecureFileHandler",
]
