import pytest


@pytest.fixture()
def suite_id():
    return ("2054", "Form Autofill")


@pytest.fixture()
def set_prefs():
    """Set prefs"""
    return []
