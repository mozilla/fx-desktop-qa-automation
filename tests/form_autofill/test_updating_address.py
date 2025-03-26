import pytest
from selenium.webdriver import Firefox, Keys

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object import AboutPrefs
from modules.page_object_autofill import AddressFill
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "122354"


def test_update_address(
    driver: Firefox,
    about_prefs_privacy: AboutPrefs,
    address_autofill: AddressFill,
    autofill_popup: AutofillPopup,
    util: Utilities,
    region: str,
):
    """
    C122354 - This test verifies that after updating and saving the autofill name field, the updated value appears in the Saved Addresses section.

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
    autofill_popup.click_doorhanger_button("save")

    # Double-click on the name field to trigger the autocomplete dropdown
    address_autofill.double_click("form-field", labels=["name"])
    # address_autofill.click_on("form-field", labels=["name"])
    autofill_popup.click_autofill_form_option()

    # Add a middle name inside the Name field
    address_autofill.click_on("form-field", labels=["name"])
    address_autofill.send_keys_to_element("form-field", "name", " Doe" + Keys.ENTER)

    # Save the updated address
    autofill_popup.click_doorhanger_button("update")

    # Navigate to settings
    about_prefs_privacy.open()
    about_prefs_privacy.open_and_switch_to_saved_addresses_popup()

    # Verify no dupe is saved
    element_list = about_prefs_privacy.get_elements("saved-addresses")
    assert len(element_list) == 1, (
        f"Expected 1 saved address, but found {len(element_list)}."
    )

    # Assert that "Doe" is present in updated entry
    elements = about_prefs_privacy.get_elements("saved-addresses-values")
    found_updated_address = any("Doe" in element.text for element in elements)
    assert found_updated_address, (
        "The value 'Doe' was not found in any of the address entries."
    )

    # Print the element that contains "Doe" for verification
    for element in elements:
        if "Doe" in element.text:
            print(f"Assertion passed: entry containing 'Doe': {element.text}")
