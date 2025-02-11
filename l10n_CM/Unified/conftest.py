import os

import pytest


@pytest.fixture()
def region():
    return os.environ.get("STARFOX_REGION", "US")


@pytest.fixture()
def add_prefs(region: str):
    return [
        ("extensions.formautofill.creditCards.reauth.optout", False),
        ("extensions.formautofill.reauth.enabled", False),
        ("browser.aboutConfig.showWarning", False),
        ("browser.search.region", region),
    ]


@pytest.fixture()
def set_prefs(add_prefs: dict):
    """Set prefs"""
    prefs = []
    prefs.extend(add_prefs)
    return prefs
