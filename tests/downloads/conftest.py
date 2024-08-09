import os

import pytest


@pytest.fixture()
def suite_id():
    return ("S29219", "Downloads")


@pytest.fixture()
def set_prefs():
    """Set prefs"""
    return []


@pytest.fixture()
def delete_files(sys_platform):
    """Remove the files after the test finishes, should work for Mac/Linux/MinGW"""

    def _delete_files():
        if sys_platform.startswith("Win"):
            if os.environ.get("GITHUB_ACTIONS") == "true":
                downloads_folder = os.path.join(
                    "C:", "Users", "runneradmin", "Downloads"
                )
        else:
            home_folder = os.environ.get("HOME")
            downloads_folder = os.path.join(home_folder, "Downloads")
        for file in os.listdir(downloads_folder):
            if file.startswith("i-9") and file.endswith(".pdf"):
                os.remove(os.path.join(downloads_folder, file))

    _delete_files()
    yield True
    _delete_files()
