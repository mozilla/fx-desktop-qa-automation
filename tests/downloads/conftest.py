import os
import subprocess
import time

import pytest

DOWNLOAD_TIMEOUT_SEC = 10.0
POLL_INTERVAL_SEC = 0.5


@pytest.fixture()
def wait_for_file_download():
    """Return a helper that blocks until a file finishes downloading."""

    def _wait_for_file_download(
        file_path, timeout=DOWNLOAD_TIMEOUT_SEC, interval=POLL_INTERVAL_SEC
    ) -> bool:
        start = time.time()
        while time.time() - start < timeout:
            if os.path.exists(file_path):
                return True
            time.sleep(interval)
        return False

    return _wait_for_file_download


@pytest.fixture()
def suite_id():
    return ("S29219", "Downloads")


@pytest.fixture()
def prefs_list(add_to_prefs_list: dict):
    """List of prefs to send to main conftest.py driver fixture."""
    prefs = []
    prefs.extend(add_to_prefs_list)
    return prefs


@pytest.fixture()
def add_to_prefs_list():
    return []


def _close_macos_windows(app_name: str) -> None:
    """Close all windows for the given macOS application via AppleScript."""
    subprocess.run(
        [
            "osascript",
            "-e",
            f'tell application "{app_name}" to close windows',
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _kill_linux_processes(process_names: tuple[str, ...]) -> None:
    """pkill a list of processes on Linux, ignoring errors."""
    for proc_name in process_names:
        subprocess.run(
            ["pkill", "-f", proc_name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


@pytest.fixture()
def close_external_apps(sys_platform):
    """
    Generic cleanup fixture for external apps that may auto-open downloads.

    Currently:
      - macOS: closes Finder windows
      - Linux: kills Archive Manager + LibreOffice processes
    """
    # Let the test run first
    yield

    if sys_platform == "Darwin":
        _close_macos_windows("Finder")

    elif sys_platform == "Linux":
        # Archive Manager
        _kill_linux_processes(
            (
                "file-roller",
                "org.gnome.ArchiveManager",
            )
        )

        # LibreOffice Writer and similar
        _kill_linux_processes(
            (
                "libreoffice",
                "libreoffice-writer",
                "soffice",
                "soffice.bin",
            )
        )
