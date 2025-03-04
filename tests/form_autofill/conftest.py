import pytest


@pytest.fixture()
def suite_id():
    return ("2054", "Form Autofill")


@pytest.fixture()
def prefs_list(add_to_prefs_list: dict):
    """List of prefs to send to main conftest.py driver fixture"""
    prefs = [
        ("extensions.formautofill.creditCards.reauth.optout", False),
        ("extensions.formautofill.reauth.enabled", False),
    ]
    prefs.extend(add_to_prefs_list)
    return prefs


@pytest.fixture()
def add_to_prefs_list():
    return []
