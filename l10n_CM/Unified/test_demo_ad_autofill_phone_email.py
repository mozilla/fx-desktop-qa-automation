import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object_autofill import AddressFill
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "2888569"


def test_demo_ad_autofill_phone_email(driver: Firefox, region: str):
    """
    C2888569 - Verify Autofill functionality when selecting an entry from the dropdown for tele/email fields
    """
    # Instantiate objects
    address_autofill = AddressFill(driver)
    address_autofill_popup = AutofillPopup(driver)
    util = Utilities()

    # Create fake data and fill it in
    address_autofill.open()
    address_autofill_data = util.fake_autofill_data(region)
    address_autofill.save_information_basic(address_autofill_data)

    # Click the "Save" button
    address_autofill_popup.click_doorhanger_button("save")

    # Double inside phone field and select a saved address entry from the dropdown
    address_autofill.double_click("form-field", labels=["tel"])

    # Click on the first element from the autocomplete dropdown
    first_item = address_autofill_popup.get_nth_element(1)
    address_autofill_popup.click_on(first_item)

    # Verify autofill data
    address_autofill.verify_autofill_data(address_autofill_data, region, util)

    # Double inside phone field and select clear form autofill
    address_autofill.double_click("form-field", labels=["tel"])
    address_autofill_popup.click_clear_form_option()

    # Double inside email field and select a saved address entry from the dropdown
    address_autofill.double_click("form-field", labels=["email"])

    # Click on the first element from the autocomplete dropdown
    first_item = address_autofill_popup.get_nth_element(1)
    address_autofill_popup.click_on(first_item)

    # Verify autofill data
    address_autofill.verify_autofill_data(address_autofill_data, region, util)
