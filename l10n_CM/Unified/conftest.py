import os
from typing import List

import pytest

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object_autofill import AddressFill, CreditCardFill
from modules.page_object_prefs import AboutPrefs
from modules.util import Utilities


@pytest.fixture()
def region():
    return os.environ.get("STARFOX_REGION", "US")


@pytest.fixture()
def add_prefs(region: str):
    return []


@pytest.fixture()
def set_prefs(add_prefs: List[tuple[str, str | bool]], region: str):
    """Set prefs"""
    prefs = [
        ("extensions.formautofill.creditCards.reauth.optout", False),
        ("extensions.formautofill.reauth.enabled", False),
        ("browser.aboutConfig.showWarning", False),
        ("browser.search.region", region),
    ]
    prefs.extend(add_prefs)
    return prefs


@pytest.fixture()
def address_autofill(driver):
    yield AddressFill(driver)


@pytest.fixture()
def address_autofill_popup(driver):
    yield AutofillPopup(driver)


@pytest.fixture()
def util():
    yield Utilities()


@pytest.fixture()
def about_prefs(driver):
    yield AboutPrefs(driver, category="privacy")


@pytest.fixture()
def about_prefs_cc_popup(driver):
    yield AboutPrefs(driver)


@pytest.fixture()
def credit_card_fill_obj(driver):
    yield CreditCardFill(driver)
