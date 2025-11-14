import subprocess

import pytest


@pytest.fixture()
def suite_id():
    return ("S29219", "Downloads")


@pytest.fixture()
def prefs_list(add_to_prefs_list: dict):
    """List of prefs to send to main conftest.py driver fixture"""
    prefs = []
    prefs.extend(add_to_prefs_list)
    return prefs


@pytest.fixture()
def add_to_prefs_list():
    return []


@pytest.fixture()
def close_file_manager(sys_platform):
    # Let the test run first
    yield

    # macOS : Finder auto-unzips directories ---
    if sys_platform == "Darwin":
        subprocess.run(
            ["osascript", "-e", 'tell application "Finder" to close windows'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    # Ubuntu / Linux : Archive Manager AND LibreOffice auto-open ZIPs ---
    elif sys_platform == "Linux":
        # Close common Ubuntu archive managers
        for proc_name in (
            "file-roller",
            "org.gnome.ArchiveManager",
        ):
            subprocess.run(
                ["pkill", "-f", proc_name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

        # Close LibreOffice Writer and related processes
        for proc_name in (
            "libreoffice",
            "libreoffice-writer",
            "soffice",
            "soffice.bin",
        ):
            subprocess.run(
                ["pkill", "-f", proc_name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
