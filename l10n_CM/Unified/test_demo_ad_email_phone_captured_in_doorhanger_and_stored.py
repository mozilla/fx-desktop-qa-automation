import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object_autofill import AddressFill
from modules.page_object_prefs import AboutPrefs
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "2886581"


def test_demo_ad_email_phone_captured_in_doorhanger_and_stored(
    driver: Firefox,
    region: str,
    address_autofill: AddressFill,
    util: Utilities,
    autofill_popup: AutofillPopup,
    about_prefs_privacy: AboutPrefs,
):
    """
    C2888704 - Verify tele/email data are captured in the Capture Doorhanger and stored in about:preferences
    """

    # create fake data and fill it in
    address_autofill.open()
    address_autofill_data = util.fake_autofill_data(region)
    address_autofill.save_information_basic(address_autofill_data)

    # The "Save address?" doorhanger is displayed
    autofill_popup.element_visible("address-save-doorhanger")

    # containing email field
    expected_email = address_autofill_data.email
    autofill_popup.element_has_text("address-doorhanger-email", expected_email)

    # containing phone field
    expected_phone = address_autofill_data.telephone
    actual_phone = autofill_popup.get_cc_doorhanger_data("address-doorhanger-phone")
    normalize_expected = util.normalize_regional_phone_numbers(expected_phone, region)
    normalized_actual = util.normalize_regional_phone_numbers(actual_phone, region)
    assert normalized_actual == normalize_expected, (
        f"Phone number mismatch for {region} | Expected: {normalize_expected}, Got: {normalized_actual}"
    )

    # Click the "Save" button
    autofill_popup.click_doorhanger_button("save")

    # Navigate to about:preferences#privacy => "Autofill" section
    about_prefs_privacy.open()
    about_prefs_privacy.switch_to_saved_addresses_popup_iframe()

    # The address saved in step 2 is listed in the "Saved addresses" modal: Email and phone
    elements = map(
        data_sanitizer,
        about_prefs_privacy.get_element("saved-addresses-values").text.split(","),
    )
    expected_values = [expected_phone, expected_email]
    found_email_phone = list(set(elements) & set(expected_values))
    assert found_email_phone, (
        "Email or phone were not found in any of the address entries!"
    )


def data_sanitizer(value: str):
    value = value.strip()
    if value[0] == "+":
        return value[1:]
    return value
