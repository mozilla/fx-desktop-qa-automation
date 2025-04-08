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
    # navigate to address form page
    address_autofill.open()

    # Create fake data, fill in the form, and press submit, no doorhanger because of private mode
    address_autofill.fill_and_save(region, door_hanger=False)
    autofill_popup.ensure_autofill_dropdown_not_visible()

    # open about:prefs#privacy and switch to saved addresses dialog panel
    about_prefs_privacy.open()
    about_prefs_privacy.open_and_switch_to_saved_addresses_popup()

    # Get all saved addresses items and filter out any false data.
    saved_address_profiles = about_prefs_privacy.get_all_saved_address_profiles()
    assert len(saved_address_profiles) == 0, (
        f"Expected 0 saved address, but found {len(saved_address_profiles)}."
    )
