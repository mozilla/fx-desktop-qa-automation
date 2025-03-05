from shutil import copyfile

import pytest

from modules.page_object import GenericPdf


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
