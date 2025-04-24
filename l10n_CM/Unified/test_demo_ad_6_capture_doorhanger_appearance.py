import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object_autofill import AddressFill
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "2886581"


def test_address_doorhanger_displayed_after_entering_valid_address(
    driver: Firefox,
    region: str,
    address_autofill: AddressFill,
    util: Utilities,
    autofill_popup: AutofillPopup,
    ad_is_live_site: str,
):
    """
    C2886581 - Verify the Capture Door hanger is displayed after entering valid Address data
    """
    if not ad_is_live_site:
        # Create fake data and fill it in
        address_autofill.open()
        # scroll to first form field
        address_autofill.scroll_to_form_field()

        address_autofill.fill_and_save(region, door_hanger=False)

        # Check "Save Address?" door hanger appears in the Address bar
        autofill_popup.element_visible("address-save-doorhanger")
    else:
        pytest.skip("Doorhanger not tested for Live Sites.")
