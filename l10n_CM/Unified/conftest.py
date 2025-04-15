import os
from json import load
from typing import List

import pytest

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object_autofill import AddressFill, CreditCardFill
from modules.page_object_prefs import AboutPrefs
from modules.util import Utilities

current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)


@pytest.fixture()
def region():
    return os.environ.get("FX_REGION", "US")


@pytest.fixture()
def site_data():
    live_site = os.environ.get("FX_SITE", None)
    # un comment to test a live site form
    # live_site = "walmart/walmart_ad"
    if live_site:
        path_to_site = parent_dir + "/constants/"
        with open(path_to_site + live_site + ".json", "r") as fp:
            live_site_data = load(fp)
            return live_site_data
    return {}


@pytest.fixture()
def url_template(site_data):
    return site_data.get("url", None)


@pytest.fixture()
def fields(site_data):
    return site_data.get("fields", None)


@pytest.fixture()
def field_mapping(site_data):
    return site_data.get("field_mapping", None)


@pytest.fixture()
def submit_button(site_data):
    submit = site_data.get("submit_button", None)
    return (
        {"submit-button": {"selectorData": submit, "strategy": "css", "groups": []}}
        if submit
        else {}
    )


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
def address_autofill(driver, url_template, fields, field_mapping, submit_button):
    af = AddressFill(
        driver, url_template=url_template, field_mapping=field_mapping, fields=fields
    )
    af.elements |= submit_button
    yield af


@pytest.fixture()
def credit_card_autofill(driver, url_template, fields, field_mapping, submit_button):
    cf = CreditCardFill(
        driver, url_template=url_template, field_mapping=field_mapping, fields=fields
    )
    cf.elements |= submit_button
    yield cf


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
