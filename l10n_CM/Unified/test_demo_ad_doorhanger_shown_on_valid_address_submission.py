import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object import AboutConfig
from modules.page_object_autofill import AddressFill
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "2886581"


def test_address_doorhanger_displayed_after_entering_valid_address(
    driver: Firefox, region: str
):
    """
    C2886581 - Verify the Capture Doorhanger is displayed after entering valid Address data
    """

    # Instantiate objects
    address_autofill = AddressFill(driver)
    address_autofill_popup = AutofillPopup(driver)
    util = Utilities()
    about_config = AboutConfig(driver)

    # Change pref value of region
    about_config.change_config_value("browser.search.region", region)

    # Create fake data and fill it in
    address_autofill.open()
    address_autofill_data = util.fake_autofill_data(region)
    address_autofill.save_information_basic(address_autofill_data)

    # Check "Save Address?" doorhanger appears in the Address bar
    address_autofill_popup.wait.until(
        lambda _: address_autofill_popup.element_visible("address-save-doorhanger")
    )
