import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object_about_pages import AboutConfig
from modules.page_object_autofill import AddressFill
from modules.page_object_prefs import AboutPrefs
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "2886581"


params = [("US", "US"), ("CA", "CA")]


@pytest.mark.parametrize("region, locale", params)
def test_us_demo_ad_email_phone_captured_in_doorhanger_and_stored(driver: Firefox, region: str, locale: str):
    """
    C2888704 - Verify tele/email data are captured in the Capture Doorhanger and stored in about:preferences
    """
    # instantiate objects
    address_autofill = AddressFill(driver)
    address_autofill_popup = AutofillPopup(driver)
    util = Utilities()
    about_config = AboutConfig(driver)

    # Change pref value of region
    about_config.change_config_value("browser.search.region", region)

    # create fake data and fill it in
    address_autofill.open()
    address_autofill_data = util.fake_autofill_data(locale)
    address_autofill.save_information_basic(address_autofill_data)

    # The "Save address?" doorhanger is displayed
    address_autofill_popup.wait.until(lambda _: address_autofill_popup.element_visible("address-save-doorhanger"))

    # click on edit
    # address_autofill_popup.click_on("address-save-doorhanger-edit")

    # containing email field
    expected_email = address_autofill_data.street_address
    with driver.context(driver.CONTEXT_CHROME):
        email_field = address_autofill_popup.get_element("address-doorhanger-email-field")
    address_autofill_popup.wait.until(lambda _: email_field.text == expected_email)

    # containing phone field


    # Click the "Save" button
    address_autofill_popup.click_doorhanger_button("save")

    # Navigate to about:preferences#privacy => "Autofill" section and click the "Saved addresses" button
    about_prefs = AboutPrefs(driver, category="privacy").open()
    about_prefs.get_element("save-and-fill-addresses").click()

    # The address saved in step 2 is listed in the "Saved addresses" modal: Email and phone

