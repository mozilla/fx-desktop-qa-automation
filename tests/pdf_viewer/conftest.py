from shutil import copyfile

import pytest


@pytest.fixture()
def suite_id():
    return ("S65", "PDF Viewer")


@pytest.fixture()
def set_prefs():
    """Set prefs"""
    return []


@pytest.fixture()
def file_name():
    return "boeing_brochure.pdf"


@pytest.fixture()
def pdf_file_path(tmp_path, file_name: str):
    loc = tmp_path / file_name
    copyfile(f"data/{file_name}", loc)
    return loc
