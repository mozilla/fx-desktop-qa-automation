import os
import time
from shutil import copyfile

import pytest

from modules.page_object import GenericPdf

DOWNLOAD_TIMEOUT_SEC = 5.0
POLL_INTERVAL_SEC = 1.0


@pytest.fixture()
def suite_id():
    return ("S65", "PDF Viewer")


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
def file_name():
    return "boeing_brochure.pdf"


@pytest.fixture()
def pdf_file_path(tmp_path, file_name: str):
    loc = tmp_path / file_name
    copyfile(f"data/{file_name}", loc)
    return loc


@pytest.fixture()
def pdf_viewer(driver, pdf_file_path):
    return GenericPdf(driver, pdf_url=f"file://{pdf_file_path}")


@pytest.fixture()
def wait_for_file_download():
    """Return a helper that blocks until a file finishes downloading."""

    def _wait_for_file_download(
        saved_pdf_path, timeout=DOWNLOAD_TIMEOUT_SEC, interval=POLL_INTERVAL_SEC
    ) -> bool:
        """Wait until file exists on disk or raise a pytest failure."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if os.path.exists(saved_pdf_path):
                initial_size = os.path.getsize(saved_pdf_path)
                time.sleep(interval)
                final_size = os.path.getsize(saved_pdf_path)
                if initial_size == final_size and final_size > 0:
                    return True
            time.sleep(interval)
        pytest.fail(f"The file was not downloaded within {timeout:.1f} seconds.")
        return None

    return _wait_for_file_download
