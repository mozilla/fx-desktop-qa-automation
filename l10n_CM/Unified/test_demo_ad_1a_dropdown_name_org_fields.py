import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object_autofill import AddressFill
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "2888556"


def test_dropdown_presence_name_organization(
    driver: Firefox,
    region: str,
    address_autofill: AddressFill,
    util: Utilities,
    autofill_popup: AutofillPopup,
):
    """
    C2888556 - Verify that the autofill dropdown is displayed  for the name and organization fields after an address was
    previously saved
    """

    # Create fake data and fill it in
    address_autofill.open()
    address_autofill_data = util.fake_autofill_data(region)
    address_autofill.save_information_basic(address_autofill_data)

    # Click the "Save" button
    autofill_popup.click_doorhanger_button("save")

    # Verify that the name and organization fields have the autofill dropdown present
    fields_to_test = ["name", "organization"]

    address_autofill.verify_autofill_dropdown_addresses(
        autofill_popup=autofill_popup, fields_to_test=fields_to_test, region=region
    )
