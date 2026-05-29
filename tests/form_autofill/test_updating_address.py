import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object import AboutPrefs
from modules.page_object_autofill import AddressFill


@pytest.fixture()
def test_case():
    return "122354"


def test_update_address(
    driver: Firefox,
    about_prefs_addresses: AboutPrefs,
    address_autofill: AddressFill,
    autofill_popup: AutofillPopup,
    region: str,
):
    """
    C122354 - This test verifies that after updating and saving the autofill name field,
    the updated value appears in the Saved Addresses section.

    Arguments:
        about_prefs_addresses: AboutPrefs instance
        address_autofill: AddressFill instance
        autofill_popup: AutofillPopup instance
        region: country code in use
    """
    address_autofill.open()

    # scroll to first form field
    address_autofill.scroll_to_form_field()

    # Create fake data, fill in the form, and press submit and save on the doorhanger
    sample_data = address_autofill.fill_and_save(region)

    # Double-click on the name field to trigger the autocomplete dropdown
    address_autofill.select_autofill_option("name")

    # Change name field value.
    new_name_value = sample_data.name + " Doe"
    setattr(sample_data, "name", new_name_value)
    address_autofill.update_form_data(sample_data, "name", new_name_value, region)

    # Navigate to settings
    about_prefs_addresses.open()

    # Verify no dupe is saved
    about_prefs_addresses.confirm_n_addresses(1)

    # Assert that "Doe" is present in updated entry
    about_prefs_addresses.element_has_text("saved-address-entry", new_name_value)
