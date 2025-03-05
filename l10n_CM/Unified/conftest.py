import os
from typing import List

import pytest

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object_autofill import AddressFill, CreditCardFill
from modules.page_object_prefs import AboutPrefs
from modules.util import Utilities


@pytest.fixture()
def region():
    return os.environ.get("FX_REGION", "US")


@pytest.fixture()
def add_to_prefs_list(region: str):
    return []


@pytest.fixture()
def prefs_list(add_to_prefs_list: List[tuple[str, str | bool]], region: str):
    """List of prefs to send to main conftest.py driver fixture"""
    prefs = [
        ("extensions.formautofill.creditCards.reauth.optout", False),
        ("extensions.formautofill.reauth.enabled", False),
        ("browser.aboutConfig.showWarning", False),
        ("browser.search.region", region),
    ]
    prefs.extend(add_to_prefs_list)
    return prefs


@pytest.fixture()
def address_autofill(driver):
    yield AddressFill(driver)


@pytest.fixture()
def autofill_popup(driver):
    yield AutofillPopup(driver)


@pytest.fixture()
def util():
    yield Utilities()


@pytest.fixture()
def about_prefs_privacy(driver):
    yield AboutPrefs(driver, category="privacy")


@pytest.fixture()
def about_prefs(driver):
    yield AboutPrefs(driver)


@pytest.fixture()
def credit_card_fill_obj(driver):
    yield CreditCardFill(driver)
