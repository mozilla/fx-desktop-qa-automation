import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object_autofill import AddressFill
from modules.page_object_prefs import AboutPrefs
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "2888701"


def test_demo_ad_name_org_captured_in_doorhanger_and_stored(
    driver: Firefox,
    region: str,
    address_autofill: AddressFill,
    util: Utilities,
    autofill_popup: AutofillPopup,
    about_prefs_privacy: AboutPrefs,
):
    """
    C2888701 - Verify name/org fields are captured in the Capture Doorhanger and stored in about:preferences
    """
    # Create fake data and fill it in
    address_autofill.open()
    address_autofill_data = address_autofill.fill_and_save(
        util, autofill_popup, door_hanger=False
    )

    # The "Save address?" doorhanger is displayed
    autofill_popup.element_visible("address-save-doorhanger")

    # containing name field
    expected_name = address_autofill_data.name
    autofill_popup.element_has_text("address-doorhanger-name", expected_name)

    # containing org field
    expected_org = address_autofill_data.organization
    autofill_popup.element_has_text("address-doorhanger-org", expected_org)

    # Click the "Save" button
    autofill_popup.click_doorhanger_button("save")

    # Navigate to about:preferences#privacy => "Autofill" section
    about_prefs_privacy.open()
    about_prefs_privacy.open_and_switch_to_saved_addresses_popup()

    # The address saved in step 2 is listed in the "Saved addresses" modal: name and organization
    saved_address_profile = about_prefs_privacy.get_all_saved_address_profiles()[0].text
    found_name_org = all(
        address_data in saved_address_profile
        for address_data in [expected_name, expected_org]
    )
    assert found_name_org, (
        "Name or organization were not found in any of the address entries!"
    )
