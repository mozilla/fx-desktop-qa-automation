from shutil import copyfile

import pytest


@pytest.fixture()
def html_filename():
    return "article_page.html"


@pytest.fixture()
def suite_id():
    return ("S2126", "Reader View")


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
def local_doc_path(tmp_path, html_filename):
    loc = tmp_path / html_filename
    copyfile(f"data/pages/{html_filename}", loc)
    return f"file://{loc}"
