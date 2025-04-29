import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object_autofill import AddressFill
from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "2888701"


def test_demo_ad_name_org_captured_in_doorhanger_and_stored(
    driver: Firefox,
    region: str,
    address_autofill: AddressFill,
    autofill_popup: AutofillPopup,
    about_prefs_privacy: AboutPrefs,
    is_live_site: str,
):
    """
    C2888701 - Verify name/org fields are captured in the Capture Doorhanger and stored in about:preferences
    """
    if not is_live_site:
        # Create fake data and fill it in
        address_autofill.open()
        # scroll to first form field
        address_autofill.scroll_to_form_field()

        address_autofill_data = address_autofill.fill_and_save(
            region, door_hanger=False
        )

        # The "Save address?" doorhanger is displayed
        autofill_popup.element_visible("address-save-doorhanger")

        # containing name and org field
        expected_fields = {
            "name": address_autofill_data.name,
            "org": address_autofill_data.organization,
        }

        # check fields in doorhanger
        for key, value in expected_fields.items():
            autofill_popup.element_has_text(f"address-doorhanger-{key}", value)

        # Click the "Save" button
        autofill_popup.click_doorhanger_button("save")

        # Navigate to about:preferences#privacy => "Autofill" section
        about_prefs_privacy.open()
        about_prefs_privacy.open_and_switch_to_saved_addresses_popup()

        # Get the first saved address profile
        saved_address_profiles = about_prefs_privacy.get_all_saved_address_profiles()
        assert saved_address_profiles, "No saved address profiles found"

        saved_address_profile = saved_address_profiles[0].text

        # Verify each field is present in the saved profile
        missing_fields = []
        for field_name, field_value in expected_fields.items():
            if field_value not in saved_address_profile:
                missing_fields.append(f"{field_name}: {field_value}")

        assert not missing_fields, (
            f"The following fields were not found in the saved address: {', '.join(missing_fields)}"
        )
    else:
        pytest.skip("Doorhanger not tested for Live Sites.")
