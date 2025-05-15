import pytest
from selenium.webdriver import Firefox

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

    # scroll to first form field
    address_autofill.scroll_to_form_field()

    # Create fake data, fill in the form, and press submit and save on the doorhanger
    sample_data = address_autofill.fill_and_save(region)

    # Double-click on the name field to trigger the autocomplete dropdown
    address_autofill.select_autofill_option("name")

    # Change name field value.
    new_name_value = sample_data.name + " Doe"
    setattr(sample_data, "name", new_name_value)
    address_autofill.update_form_data(sample_data, "name", new_name_value)

    # Navigate to settings
    about_prefs_privacy.open()
    about_prefs_privacy.open_and_switch_to_saved_addresses_popup()

    # Verify no dupe is saved
    saved_addresses = about_prefs_privacy.get_all_saved_address_profiles()
    assert len(saved_addresses) == 1, (
        f"Expected 1 saved address, but found {len(saved_addresses)}."
    )

    # Assert that "Doe" is present in updated entry
    found_updated_address = any(
        new_name_value in element.text for element in saved_addresses
    )
    assert found_updated_address, (
        "The new name was not found in any of the address entries."
    )
