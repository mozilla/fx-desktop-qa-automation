import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object_autofill import CreditCardFill
from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "2886597"


def test_demo_cc_data_captured_in_doorhanger_and_stored(
    driver: Firefox,
    region: str,
    credit_card_autofill: CreditCardFill,
    autofill_popup: AutofillPopup,
    about_prefs_privacy: AboutPrefs,
    is_live_site: str,
):
    """
    C2889999 - Verify credit card data is captured in the Capture Doorhanger and stored in about:preferences
    """
    if not is_live_site:
        # Navigate to page
        credit_card_autofill.open()

        # scroll to first form field
        credit_card_autofill.scroll_to_form_field()

        # Fill data
        credit_card_sample_data = credit_card_autofill.fill_and_save(door_hanger=False)

        # The "Save credit card?" doorhanger is displayed
        assert autofill_popup.element_visible(
            "doorhanger-save-button"
        ), "Credit card save doorhanger is not visible"

        # Verify Credit Card Doorhanger Data
        doorhanger_text = autofill_popup.get_cc_doorhanger_data("cc-doorhanger-data")
        assert (
            credit_card_sample_data.card_number[-4:] in doorhanger_text
        ), f"Expected last 4 digits '{credit_card_sample_data.card_number[-4:]}' but not found."
        assert (
            credit_card_sample_data.name in doorhanger_text
        ), f"Expected name '{credit_card_sample_data.name}' but not found."
        assert (
            credit_card_sample_data.cvv not in doorhanger_text
        ), f"CVV '{credit_card_sample_data.cvv}' should not be saved, but found in doorhanger."

        # Click the "Save" button using click_doorhanger_button
        autofill_popup.click_doorhanger_button("save")

        # Navigate to about:preferences#privacy => "Autofill" section
        about_prefs_privacy.open()
        about_prefs_privacy.open_and_switch_to_saved_payments_popup()

        # Get stored values
        saved_cc_profiles = about_prefs_privacy.get_all_saved_cc_profiles()
        assert saved_cc_profiles, "No saved cc profiles found"

        saved_cc_profile = [x.strip() for x in saved_cc_profiles[0].text.split(",")]

        # Validate stored values match expected values
        assert saved_cc_profile[
            0
        ].endswith(
            credit_card_sample_data.card_number[-4:]
        ), f"Expected last 4 digits '{credit_card_sample_data.card_number[-4:]}' but got '{saved_cc_profile[0]}'"
        assert (
            saved_cc_profile[1] == credit_card_sample_data.name
        ), f"Expected name '{credit_card_sample_data.name}' but got '{saved_cc_profile[1]}'"
        assert (
            credit_card_sample_data.cvv not in saved_cc_profile
        ), f"CVV '{credit_card_sample_data.cvv}' should not be saved, but found in stored values."
    else:
        pytest.skip("Doorhanger not tested for Live Sites.")
