import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object_autofill import AddressFill
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "2886581"


country_code = "US"


def test_us_demo_address_doorhanger_displayed_after_entering_valid_address(driver: Firefox):
    """
    C2886581, Verify the Capture Doorhanger is displayed after entering valid Address data
    """
    # instantiate objects
    address_autofill = AddressFill(driver).open()
    address_autofill_popup = AutofillPopup(driver)
    util = Utilities()

    # create fake data and fill it in
    address_autofill_data = util.fake_autofill_data(country_code)
    address_autofill.save_information_basic(address_autofill_data)

    # check "Save Address?" doorhanger appears in the Address bar
    address_autofill_popup.wait.until(lambda _: address_autofill_popup.element_visible("address-save-doorhanger"))
