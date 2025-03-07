import pytest
from selenium.webdriver import Firefox, Keys

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object import AboutPrefs
from modules.page_object_autofill import AddressFill
from modules.util import BrowserActions, Utilities

COUNTRY_CODE = "US"


@pytest.fixture()
def test_case():
    return "122354"


def test_update_address(driver: Firefox):
    """
    C122354 - This test verifies that after updating and saving the autofill name field, the updated value appears in the Saved Addresses section.
    """
    # Instantiate objects and open the navigation page
    address_form_fields = AddressFill(driver).open()
    autofill_popup_panel = AutofillPopup(driver)
    util = Utilities()
    browser_action_obj = BrowserActions(driver)

    # Create fake data, fill in the form, and press submit and save on the doorhanger
    autofill_sample_data = util.fake_autofill_data(COUNTRY_CODE)
    address_form_fields.save_information_basic(autofill_sample_data)
    autofill_popup_panel.click_doorhanger_button("save")

    # Double-click on the name field to trigger the autocomplete dropdown
    address_form_fields.double_click("form-field", labels=["name"])
    address_form_fields.click_on("form-field", labels=["name"])
    autofill_popup_panel.click_autofill_form_option()

    # Add a middle name inside the Name field
    address_form_fields.click_on("form-field", labels=["name"])
    address_form_fields.send_keys_to_element("form-field", "name", " Doe" + Keys.ENTER)

    # Save the updated address
    autofill_popup_panel.click_doorhanger_button("update")

    # Navigate to settings
    about_prefs = AboutPrefs(driver, category="privacy").open()
    iframe = about_prefs.get_saved_addresses_popup_iframe()
    browser_action_obj.switch_to_iframe_context(iframe)

    # Verify no dupe is saved
    element_list = about_prefs.get_elements("saved-addresses")
    assert len(element_list) == 1, (
        f"Expected 1 saved address, but found {len(element_list)}."
    )
    print("Assertion passed: There is exactly 1 saved address.")

    # Assert that "Doe" is present in updated entry
    elements = about_prefs.get_elements("saved-addresses-values")
    found_updated_address = any("Doe" in element.text for element in elements)
    assert found_updated_address, (
        "The value 'Doe' was not found in any of the address entries."
    )

    # Print the element that contains "Doe" for verification
    for element in elements:
        if "Doe" in element.text:
            print(f"Assertion passed: entry containing 'Doe': {element.text}")
