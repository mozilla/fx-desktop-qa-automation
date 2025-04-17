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
def address_autofill(driver, url_template, fields, field_mapping):
    return AddressFill(
        driver, url_template=url_template, field_mapping=field_mapping, fields=fields
    )


@pytest.fixture()
def credit_card_autofill(driver, url_template, fields, field_mapping):
    return CreditCardFill(
        driver, url_template=url_template, field_mapping=field_mapping, fields=fields
    )


@pytest.fixture()
def autofill_popup(driver):
    return AutofillPopup(driver)


@pytest.fixture()
def util():
    return Utilities()


@pytest.fixture()
def about_prefs_privacy(driver):
    return AboutPrefs(driver, category="privacy")


@pytest.fixture()
def about_prefs(driver):
    return AboutPrefs(driver)


@pytest.fixture()
def populate_saved_payments(
    about_prefs_privacy: AboutPrefs, util: Utilities, region: str
):
    """Fixture to add cc data through saved payments method."""
    # Go to about:preferences#privacy and open Saved Payment Methods
    about_prefs_privacy.open()
    about_prefs_privacy.open_and_switch_to_saved_payments_popup()

    # Save CC information using fake data
    credit_card_sample_data = util.fake_credit_card_data(region)

    # Add a new CC profile
    about_prefs_privacy.click_add_on_dialog_element()
    about_prefs_privacy.add_entry_to_saved_payments(credit_card_sample_data)
    return credit_card_sample_data


@pytest.fixture()
def populate_saved_addresses(
    about_prefs_privacy: AboutPrefs, util: Utilities, region: str
):
    """Fixture to add cc data through saved payments method."""
    # Go to about:preferences#privacy and open Saved Addresses Methods
    about_prefs_privacy.open()
    about_prefs_privacy.open_and_switch_to_saved_addresses_popup()

    # Save address information using fake data
    address_data_sample_data = util.fake_autofill_data(region)

    # Add a new address profile
    about_prefs_privacy.click_add_on_dialog_element()
    about_prefs_privacy.add_entry_to_saved_addresses(address_data_sample_data)
    return address_data_sample_data


@pytest.fixture()
def fill_and_save_address(
    address_autofill: AddressFill, url_template: str | None, region: str, request
):
    """
    Fixture to populate address entry depending on whether the url is a live site.
    If live site, populate data through about:prefs, if not fill directly through page.
    """
    if url_template:
        return request.getfixturevalue("populate_saved_addresses")
    address_autofill.open()
    return address_autofill.fill_and_save(region)


@pytest.fixture()
def fill_and_save_payments(
    credit_card_autofill: CreditCardFill, url_template: str | None, region: str, request
):
    """
    Fixture to populate cc entry depending on whether the url is a live site.
    If live site, populate data through about:prefs, if not fill directly through page.
    """
    if url_template:
        return request.getfixturevalue("populate_saved_payments")
    credit_card_autofill.open()
    return credit_card_autofill.fill_and_save(region)
