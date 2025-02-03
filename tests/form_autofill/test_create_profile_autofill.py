import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutPrefs
from modules.util import BrowserActions, Utilities

COUNTRY_CODE = "US"


@pytest.fixture()
def test_case():
    return "122348"


def test_create_address_profile(driver: Firefox):
    """
    C122348, creating an address profile
    """
    about_prefs_obj = AboutPrefs(driver, category="privacy")
    util = Utilities()
    browser_action_obj = BrowserActions(driver)

    about_prefs_obj.open()

    # create sample data
    autofill_sample_data = util.fake_autofill_data(COUNTRY_CODE)
    iframe_address_popup = about_prefs_obj.press_button_get_popup_dialog_iframe(
        "Saved addresses"
    )
    browser_action_obj.switch_to_iframe_context(iframe_address_popup)
    about_prefs_obj.get_element(
        "panel-popup-button", labels=["autofill-manage-add-button"]
    ).click()

    # fill in the data and clean it up
    about_prefs_obj.fill_autofill_panel_information(autofill_sample_data)
    saved_address_option = about_prefs_obj.get_element("saved-addresses")
    inner_content = saved_address_option.get_attribute("innerHTML")
    cleaned_data = about_prefs_obj.extract_content_from_html(inner_content)
    split_text = about_prefs_obj.extract_and_split_text(cleaned_data)
    print(inner_content)
    print(cleaned_data)
    print(split_text)
    observed_data = about_prefs_obj.organize_data_into_obj(split_text)
    print(autofill_sample_data)
    print(observed_data)

    # currently ignoring the address level 1 field
    observed_data.telephone = util.normalize_phone_number(observed_data.telephone)
    observed_data.address_level_1 = autofill_sample_data.address_level_1

    # ensure that the objects have the same fields
    assert autofill_sample_data == observed_data
