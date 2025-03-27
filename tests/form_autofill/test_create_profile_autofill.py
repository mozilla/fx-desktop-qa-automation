import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutPrefs
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "122348"


def test_create_address_profile(
    driver: Firefox, about_prefs_privacy: AboutPrefs, util: Utilities, region: str
):
    """
    C122348, creating an address profile

    Arguments:
        about_prefs_privacy: AboutPrefs instance (privacy category)
        util: Utilities instance
        region: country code in use
    """
    about_prefs_privacy.open()

    # create sample data
    autofill_sample_data = util.fake_autofill_data(region)

    # switch to saved addresses panel
    about_prefs_privacy.open_and_switch_to_saved_addresses_popup()
    about_prefs_privacy.click_add_on_dialog_element()

    # add entry to saved addresses
    about_prefs_privacy.add_entry_to_saved_addresses(autofill_sample_data)

    elements = about_prefs_privacy.get_all_saved_address_profiles()
    about_prefs_privacy.double_click(elements[0])
    observed_data = about_prefs_privacy.extract_address_data_from_saved_addresses_entry(
        util, region
    )

    # ensure that the objects have the same fields
    assert autofill_sample_data == observed_data
