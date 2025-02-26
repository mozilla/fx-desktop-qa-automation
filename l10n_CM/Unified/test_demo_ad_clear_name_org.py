import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object_autofill import AddressFill
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "2888560"


def test_demo_ad_clear_name_org(driver: Firefox, region: str, address_autofill: AddressFill, util: Utilities):
    """
    C2888560 - Verify clear functionality after selecting an entry from name/org fields
    """
    # Instantiate objects
    address_autofill_popup = AutofillPopup(driver)

    # Create fake data and fill it in
    address_autofill.open()
    address_autofill_data = util.fake_autofill_data(region)
    address_autofill.save_information_basic(address_autofill_data)

    # Click the "Save" button
    address_autofill_popup.click_doorhanger_button("save")

    # Double inside Name field and select a saved address entry from the dropdown
    address_autofill.double_click("form-field", labels=["name"])

    # Click on the first element from the autocomplete dropdown
    first_item = address_autofill_popup.get_nth_element(1)
    address_autofill_popup.click_on(first_item)

    # Double inside Name field and select clear form autofill
    address_autofill.double_click("form-field", labels=["name"])
    address_autofill_popup.click_clear_form_option()