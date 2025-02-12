import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object_about_pages import AboutConfig
from modules.page_object_autofill import AddressFill
from modules.page_object_prefs import AboutPrefs
from modules.util import Utilities, BrowserActions


@pytest.fixture()
def test_case():
    return "2886581"


def test_demo_ad_email_phone_captured_in_doorhanger_and_stored(driver: Firefox, region: str
                                                               ):
    """
    C2888704 - Verify tele/email data are captured in the Capture Doorhanger and stored in about:preferences
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

    # containing email field
    expected_email = address_autofill_data.email
    address_autofill_popup.element_has_text("address-doorhanger-email", expected_email)

    # containing phone field
    expected_phone = address_autofill_data.telephone
    with driver.context(driver.CONTEXT_CHROME):
        actual_phone = address_autofill_popup.get_element("address-doorhanger-phone").text
    normalize_expected = util.normalize_phone_number(expected_phone)
    normalized_actual = util.normalize_phone_number(actual_phone)
    assert normalized_actual == normalize_expected

    # Click the "Save" button
    address_autofill_popup.click_doorhanger_button("save")

    # Navigate to about:preferences#privacy => "Autofill" section
    about_prefs = AboutPrefs(driver, category="privacy").open()
    iframe = about_prefs.get_save_addresses_popup_iframe()
    browser_action_obj.switch_to_iframe_context(iframe)

    # The address saved in step 2 is listed in the "Saved addresses" modal: Email and phone
    elements = about_prefs.get_elements("saved-addresses-values")
    expected_values = [expected_phone, expected_email]
    found_email_phone = any(
        all(value in element.text for value in expected_values)
        for element in elements
    )
    assert (
        found_email_phone
    ), "Email or phone were not found in any of the address entries!"
