import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object_autofill import AddressFill
from modules.page_object_prefs import AboutPrefs
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "2886581"


country_code = "US"


def test_us_demo_address_email_phone_captured_in_doorhanger_and_stored(driver: Firefox):
    """
    C2888704 - Verify tele/email data are captured in the Capture Doorhanger and stored in about:preferences
    """
    # instantiate objects
    address_autofill = AddressFill(driver).open()
    address_autofill_popup = AutofillPopup(driver)
    util = Utilities()

    # create fake data and fill it in
    address_autofill_data = util.fake_autofill_data(country_code)
    address_autofill.save_information_basic(address_autofill_data)

    # The "Save address?" doorhanger is displayed containing: Email and phone
    address_autofill_popup.wait.until(lambda _: address_autofill_popup.element_visible("address-save-doorhanger"))


    # Click the "Save" button
    address_autofill_popup.click_doorhanger_button("save")

    # Navigate to about:preferences#privacy => "Autofill" section and click the "Saved addresses" button
    about_prefs = AboutPrefs(driver, category="privacy").open()
    about_prefs.get_element("save-and-fill-addresses").click()

    # The address saved in step 2 is listed in the "Saved addresses" modal: Email and phone

