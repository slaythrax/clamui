# ClamUI Scanner Base Module
"""
Shared utilities for ClamAV scanner implementations.

This module provides common functionality used by both Scanner (clamscan) and
DaemonScanner (clamdscan) to avoid code duplication:
- Process communication with cancellation support
- Process termination with graceful shutdown
- Scan log saving
- Error result creation
"""

import logging
import subprocess
from collections.abc import Callable

from .log_manager import LogEntry, LogManager
from .scanner_types import ScanResult, ScanStatus

logger = logging.getLogger(__name__)

# Timeout constants (seconds)
TERMINATE_GRACE_TIMEOUT = 5  # Time to wait after SIGTERM before SIGKILL
KILL_WAIT_TIMEOUT = 2  # Time to wait after SIGKILL


def communicate_with_cancel_check(
    process: subprocess.Popen,
    is_cancelled: Callable[[], bool],
) -> tuple[str, str, bool]:
    """
    Communicate with process while checking for cancellation.

    Uses a polling loop with timeout to allow periodic cancellation checks.
    This prevents the scan thread from blocking indefinitely on communicate().

    Args:
        process: The subprocess to communicate with.
        is_cancelled: Callable that returns True if operation was cancelled.

    Returns:
        Tuple of (stdout, stderr, was_cancelled).
    """
    stdout_parts: list[str] = []
    stderr_parts: list[str] = []

    while True:
        if is_cancelled():
            # Terminate process and collect any remaining output
            try:
                process.terminate()
                stdout, stderr = process.communicate(timeout=2.0)
                stdout_parts.append(stdout or "")
                stderr_parts.append(stderr or "")
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            return "".join(stdout_parts), "".join(stderr_parts), True

        try:
            stdout, stderr = process.communicate(timeout=0.5)
            stdout_parts.append(stdout or "")
            stderr_parts.append(stderr or "")
            return "".join(stdout_parts), "".join(stderr_parts), False
        except subprocess.TimeoutExpired:
            continue  # Loop again, check cancel flag


def cleanup_process(process: subprocess.Popen | None) -> None:
    """
    Ensure a subprocess is properly terminated and cleaned up.

    Args:
        process: The subprocess to clean up, or None.
    """
    if process is None:
        return

    try:
        if process.poll() is None:  # Only kill if still running
            process.kill()
        process.wait(timeout=KILL_WAIT_TIMEOUT)
    except (OSError, ProcessLookupError, subprocess.TimeoutExpired):
        pass


def terminate_process_gracefully(process: subprocess.Popen | None) -> None:
    """
    Terminate a process with graceful shutdown escalation.

    First sends SIGTERM, then escalates to SIGKILL if the process
    doesn't respond within the grace period.

    Args:
        process: The subprocess to terminate, or None.
    """
    if process is None:
        return

    # Step 1: SIGTERM (graceful)
    try:
        process.terminate()
    except (OSError, ProcessLookupError):
        # Process already gone
        return

    # Step 2: Wait for graceful termination
    try:
        process.wait(timeout=TERMINATE_GRACE_TIMEOUT)
    except subprocess.TimeoutExpired:
        # Step 3: SIGKILL (forceful)
        logger.warning("Process didn't terminate gracefully, killing")
        try:
            process.kill()
            process.wait(timeout=KILL_WAIT_TIMEOUT)
        except (OSError, ProcessLookupError, subprocess.TimeoutExpired):
            pass  # Best effort


def save_scan_log(
    log_manager: LogManager,
    result: ScanResult,
    duration: float,
    suffix: str = "",
    scheduled: bool = False,
) -> None:
    """
    Save scan result to log.

    Args:
        log_manager: The LogManager instance to save to.
        result: The scan result.
        duration: Scan duration in seconds.
        suffix: Optional suffix for summary (e.g., "(daemon)").
        scheduled: Whether this was a scheduled scan.
    """
    # Map ScanStatus to string
    status_map = {
        ScanStatus.CLEAN: "clean",
        ScanStatus.INFECTED: "infected",
        ScanStatus.CANCELLED: "cancelled",
        ScanStatus.ERROR: "error",
    }
    scan_status = status_map.get(result.status, "error")

    # Convert threat details to dicts for the factory method
    threat_dicts = [
        {"file_path": t.file_path, "threat_name": t.threat_name} for t in result.threat_details
    ]

    entry = LogEntry.from_scan_result_data(
        scan_status=scan_status,
        path=result.path,
        duration=duration,
        scanned_files=result.scanned_files,
        scanned_dirs=result.scanned_dirs,
        infected_count=result.infected_count,
        threat_details=threat_dicts,
        error_message=result.error_message,
        stdout=result.stdout,
        suffix=suffix,
        scheduled=scheduled,
    )
    log_manager.save_log(entry)


def create_error_result(
    path: str,
    error_message: str,
    stderr: str = "",
) -> ScanResult:
    """
    Create a ScanResult for an error condition.

    Args:
        path: The path that was being scanned.
        error_message: The error message.
        stderr: Optional stderr content.

    Returns:
        A ScanResult with ERROR status.
    """
    return ScanResult(
        status=ScanStatus.ERROR,
        path=path,
        stdout="",
        stderr=stderr or error_message,
        exit_code=-1,
        infected_files=[],
        scanned_files=0,
        scanned_dirs=0,
        infected_count=0,
        error_message=error_message,
        threat_details=[],
    )


def create_cancelled_result(
    path: str,
    stdout: str = "",
    stderr: str = "",
    exit_code: int = -1,
    scanned_files: int = 0,
    scanned_dirs: int = 0,
) -> ScanResult:
    """
    Create a ScanResult for a cancelled operation.

    Args:
        path: The path that was being scanned.
        stdout: Captured stdout.
        stderr: Captured stderr.
        exit_code: The process exit code.
        scanned_files: Number of files scanned before cancellation.
        scanned_dirs: Number of directories scanned before cancellation.

    Returns:
        A ScanResult with CANCELLED status.
    """
    return ScanResult(
        status=ScanStatus.CANCELLED,
        path=path,
        stdout=stdout,
        stderr=stderr,
        exit_code=exit_code,
        infected_files=[],
        scanned_files=scanned_files,
        scanned_dirs=scanned_dirs,
        infected_count=0,
        error_message="Scan cancelled by user",
        threat_details=[],
    )
