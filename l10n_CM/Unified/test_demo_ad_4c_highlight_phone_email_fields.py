import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.classes.autofill_base import AutofillAddressBase
from modules.page_object_autofill import AddressFill
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "2888570"


def test_address_yellow_highlight_address_fields(
    driver: Firefox,
    region: str,
    address_autofill: AddressFill,
    util: Utilities,
    autofill_popup: AutofillPopup,
    fill_and_save_address: AutofillAddressBase,
):
    """
    C2888570 - Verify the yellow highlight appears on autofilled fields for the email and phone fields.
    """
    if address_autofill.is_field_present("email"):
        # Create fake data and fill it in
        address_autofill.open()

        # Double click inside name field and select a saved address entry from the dropdown
        address_autofill.click_form_field("email")
        autofill_popup.ensure_autofill_dropdown_visible()

        # Click on the first element from the autocomplete dropdown
        autofill_popup.select_nth_element(1)

        field_to_test = ["email", "telephone"]
        # Verify the address fields are highlighted
        address_autofill.verify_field_highlight(
            fields_to_test=field_to_test,
            expected_highlighted_fields=field_to_test,
            region=region,
        )
