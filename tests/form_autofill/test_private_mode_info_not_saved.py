import pytest
from selenium.webdriver import Firefox

from modules.browser_object import AutofillPopup
from modules.page_object import AboutPrefs
from modules.page_object_autofill import AddressFill
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "122587"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [
        ("extensions.formautofill.creditCards.reauth.optout", False),
        ("extensions.formautofill.reauth.enabled", False),
        ("browser.privatebrowsing.autostart", True),
    ]


def test_private_mode_info_not_saved(
    driver: Firefox,
    about_prefs_privacy: AboutPrefs,
    address_autofill: AddressFill,
    autofill_popup: AutofillPopup,
    util: Utilities,
    region: str,
):
    """
    C122587 - Autofill data not saved in private mode.
    This only tests the last part of the written TC - case should be divided

    Arguments:
        about_prefs_privacy: AboutPrefs instance (privacy category)
        address_autofill: AddressFill instance
        autofill_popup: AutofillPopup instance
        util: Utilities instance
        region: country code in use
    """

    address_autofill.open()

    # Create fake data, fill in the form, and press submit and save on the doorhanger
    autofill_sample_data = util.fake_autofill_data(region)
    address_autofill.save_information_basic(autofill_sample_data)
    autofill_popup.ensure_autofill_dropdown_not_visible()

    about_prefs_privacy.open()

    about_prefs_privacy.open_and_switch_to_saved_addresses_popup()
    # Get all saved addresses items and filter out any false data.
    element_list = list(
        filter(
            lambda d: len(d.get_attribute("innerHTML")) > 1,
            about_prefs_privacy.get_elements("saved-addresses"),
        )
    )
    assert len(element_list) == 0, (
        f"Expected 0 saved address, but found {len(element_list)}."
    )
