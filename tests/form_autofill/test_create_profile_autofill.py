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
    about_prefs_privacy.open_and_switch_to_saved_addresses_popup()
    about_prefs_privacy.get_element(
        "panel-popup-button", labels=["autofill-manage-add-button"]
    ).click()

    # fill in the data and clean it up
    about_prefs_privacy.add_entry_to_saved_addresses(autofill_sample_data)
    about_prefs_privacy.switch_to_saved_addresses_popup_iframe()
    saved_address_option = about_prefs_privacy.get_element("saved-addresses")
    inner_content = saved_address_option.get_attribute("innerHTML")
    cleaned_data = about_prefs_privacy.extract_content_from_html(inner_content)
    split_text = about_prefs_privacy.extract_and_split_text(cleaned_data)
    observed_data = about_prefs_privacy.organize_data_into_obj(split_text)

    # currently ignoring the address level 1 field
    observed_data.telephone = util.normalize_phone_number(observed_data.telephone)
    observed_data.country = autofill_sample_data.country
    observed_data.address_level_1 = autofill_sample_data.address_level_1

    # ensure that the objects have the same fields
    assert autofill_sample_data == observed_data
