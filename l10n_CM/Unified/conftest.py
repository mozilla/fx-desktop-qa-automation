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
    return os.environ.get("FX_REGION")


@pytest.fixture()
def live_site():
    return os.environ.get("FX_SITE")


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
def ad_site_data(live_site):
    ad_live_site = f"{live_site}/{live_site}_ad"
    if live_site:
        path_to_site = parent_dir + "/constants/"
        with open(path_to_site + ad_live_site + ".json", "r") as fp:
            live_site_data = load(fp)
            return live_site_data
    return {}


@pytest.fixture()
def ad_url_template(ad_site_data):
    return ad_site_data.get("url", None)


@pytest.fixture()
def cc_site_data(live_site):
    cc_live_site = f"{live_site}/{live_site}_cc"
    if live_site:
        path_to_site = parent_dir + "/constants/"
        with open(path_to_site + cc_live_site + ".json", "r") as fp:
            live_site_data = load(fp)
            return live_site_data
    return {}


@pytest.fixture()
def cc_url_template(cc_site_data):
    return cc_site_data.get("url", None)


@pytest.fixture()
def ad_form_field(ad_site_data):
    selector = ad_site_data.get("form_field", None)
    return (
        {"form-field": {"selectorData": selector, "strategy": "css", "groups": []}}
        if selector
        else {}
    )


@pytest.fixture()
def cc_form_field(cc_site_data):
    selector = cc_site_data.get("form_field", None)
    return (
        {"form-field": {"selectorData": selector, "strategy": "css", "groups": []}}
        if selector
        else {}
    )


@pytest.fixture()
def address_autofill(driver, ad_site_data, ad_form_field):
    af = AddressFill(
        driver,
        url_template=ad_site_data.get("url"),
        field_mapping=ad_site_data.get("field_mapping"),
        fields=ad_site_data.get("fields"),
    )
    af.elements |= ad_form_field
    return af


@pytest.fixture()
def credit_card_autofill(driver, cc_site_data, cc_form_field):
    cf = CreditCardFill(
        driver,
        url_template=cc_site_data.get("url"),
        field_mapping=cc_site_data.get("field_mapping"),
        fields=cc_site_data.get("fields"),
    )
    cf.elements |= cc_form_field
    return cf


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
    address_autofill: AddressFill, ad_site_data, region: str, request
):
    """
    Fixture to populate address entry depending on whether the url is a live site.
    If live site, populate data through about:prefs, if not fill directly through page.
    """
    if ad_site_data.get("url"):
        return request.getfixturevalue("populate_saved_addresses")
    address_autofill.open()
    return address_autofill.fill_and_save(region)


@pytest.fixture()
def fill_and_save_payments(
    credit_card_autofill: CreditCardFill, cc_site_data, region: str, request
):
    """
    Fixture to populate cc entry depending on whether the url is a live site.
    If live site, populate data through about:prefs, if not fill directly through page.
    """
    if cc_site_data.get("url"):
        return request.getfixturevalue("populate_saved_payments")
    credit_card_autofill.open()
    return credit_card_autofill.fill_and_save(region)
