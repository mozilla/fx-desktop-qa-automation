import os
import time

import pytest

from modules.browser_object import PrintPreview

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
    return ("S73", "Printing UI Modernization")


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
def print_preview(driver):
    return PrintPreview(driver)
