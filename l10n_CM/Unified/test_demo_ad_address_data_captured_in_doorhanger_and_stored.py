import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object_autofill import AddressFill
from modules.page_object_prefs import AboutPrefs
from modules.util import BrowserActions, Utilities


@pytest.fixture()
def test_case():
    return "2888703"


def test_demo_ad_address_data_captured_in_doorhanger_and_stored(
    driver: Firefox, region: str
):
    """
    C2888703 - Verify Address data are captured in the Capture Doorhanger and stored in about:preferences
    """
    # instantiate objects
    address_autofill = AddressFill(driver)
    address_autofill_popup = AutofillPopup(driver)
    util = Utilities()
    browser_action_obj = BrowserActions(driver)

    # create fake data and fill it in
    address_autofill.open()
    address_autofill_data = util.fake_autofill_data(region)
    address_autofill.save_information_basic(address_autofill_data)

    # The "Save address?" doorhanger is displayed
    address_autofill_popup.element_visible("address-save-doorhanger")

    # containing Street Address field
    expected_street_add = address_autofill_data.street_address
    address_autofill_popup.element_has_text(
        "address-doorhanger-street", expected_street_add
    )

    # containing City field
    expected_city = address_autofill_data.address_level_2
    address_autofill_popup.element_has_text("address-doorhanger-city", expected_city)

    expected_state = address_autofill_data.address_level_1
    if region not in ["FR", "DE"]:
        state_abbreviation = util.get_state_province_abbreviation(expected_state)
        address_autofill_popup.element_has_text(
            "address-doorhanger-state", state_abbreviation
        )

    # Verify Zip Code field (Different selector for DE/FR)
    expected_zip = address_autofill_data.postal_code
    zip_selector = (
        "address-doorhanger-zip-other"
        if region in ["FR", "DE"]
        else "address-doorhanger-zip"
    )
    address_autofill_popup.element_has_text(zip_selector, expected_zip)

    # containing Country field
    expected_country = address_autofill_data.country
    address_autofill_popup.element_has_text(
        "address-doorhanger-country", expected_country
    )

    # Click the "Save" button
    address_autofill_popup.click_doorhanger_button("save")

    # Navigate to about:preferences#privacy => "Autofill" section
    about_prefs = AboutPrefs(driver, category="privacy").open()
    iframe = about_prefs.get_save_addresses_popup_iframe()
    browser_action_obj.switch_to_iframe_context(iframe)

    # Verify saved addresses
    elements = about_prefs.get_elements("saved-addresses-values")

    # Expected values for verification
    expected_values = [
        expected_street_add,
        expected_city,
        expected_zip,
        expected_country,
    ]
    if region not in ["FR", "DE"]:
        expected_values.insert(2, expected_state)

    # Check if all expected values exist in any saved address
    found_address_data = any(
        all(value in element.text for value in expected_values) for element in elements
    )
    assert found_address_data, "Street, city, state (if applicable), zip, or country were not found in any of the address entries!"
