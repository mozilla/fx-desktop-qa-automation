import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object_autofill import AddressFill
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "2888559"


def test_address_yellow_highlight_on_name_organization_fields(
    driver: Firefox,
    region: str,
    util: Utilities,
    address_autofill: AddressFill,
    autofill_popup: AutofillPopup,
):
    """
    C2888559 - Verify the yellow highlight appears on autofilled fields for name and organization.
    """

    # Create fake data and fill it in
    address_autofill.open()
    address_autofill_data = util.fake_autofill_data(region)
    address_autofill.save_information_basic(address_autofill_data)

    # Click the "Save" button
    autofill_popup.click_doorhanger_button("save")

    # Double click inside phone field and select a saved address entry from the dropdown
    address_autofill.double_click("form-field", labels=["name"])

    # Click on the first element from the autocomplete dropdown
    first_item = autofill_popup.get_nth_element(1)
    autofill_popup.click_on(first_item)

    # Verify the name and organization fields are highlighted
    address_autofill.verify_field_yellow_highlights(
        fields_to_test=["name", "organization"],
        expected_highlighted_fields=["name", "organization"],
    )
