import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object_autofill import AddressFill
from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "2888704"


def test_demo_ad_email_phone_captured_in_doorhanger_and_stored(
    driver: Firefox,
    region: str,
    address_autofill: AddressFill,
    autofill_popup: AutofillPopup,
    about_prefs_privacy: AboutPrefs,
    is_live_site: str,
):
    """
    C2888704 - Verify phone/email data are captured in the Capture Doorhanger and stored in about:preferences
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

        # containing address fields
        expected_fields = {
            "email": address_autofill_data.email,
            "phone": address_autofill_data.telephone,
        }

        # check fields in doorhanger
        for key, value in expected_fields.items():
            autofill_popup.element_has_text(f"address-doorhanger-{key}", value)

        # Click the "Save" button
        autofill_popup.click_doorhanger_button("save")

        # Navigate to about:preferences#privacy => "Autofill" section
        about_prefs_privacy.open()
        about_prefs_privacy.open_and_switch_to_saved_addresses_popup()

        # The Fx 154 saved-address tile only shows a name + address summary, so read
        # the stored email/telephone fields from the address edit view.
        stored = about_prefs_privacy.get_stored_address_values()
        assert stored.get("name"), "No saved address profile found"

        expected_stored = {
            "email": address_autofill_data.email,
            "tel": address_autofill_data.telephone,
        }
        missing_fields = [
            f"{field_id}: {value}"
            for field_id, value in expected_stored.items()
            if value not in (stored.get(field_id) or "")
        ]

        assert not missing_fields, (
            f"The following fields were not found in the saved address: {', '.join(missing_fields)}"
        )
    else:
        pytest.skip("Doorhanger not tested for Live Sites.")
