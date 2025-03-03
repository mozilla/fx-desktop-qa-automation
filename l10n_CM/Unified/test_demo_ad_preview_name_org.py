import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object_autofill import AddressFill
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "2888557"


def test_demo_ad_preview_name_org(
    driver: Firefox,
    region: str,
    address_autofill: AddressFill,
    util: Utilities,
    autofill_popup: AutofillPopup
):
    """
    C2888557 - Verify Autofill Preview on hover over dropdown entries for name/org fields
    """
    # Create fake data and fill it in
    address_autofill.open()
    address_autofill_data = util.fake_autofill_data(region)
    address_autofill.save_information_basic(address_autofill_data)

    # Click the "Save" button
    autofill_popup.click_doorhanger_button("save")

    # Double-click inside Name field and hover the mouse over any saved address entry in the dropdown (without selecting it).
    address_autofill.double_click("form-field", labels=["name"])
    # Get the first element from the autocomplete dropdown
    first_item = autofill_popup.get_nth_element(1)
    actual_value = autofill_popup.hover(first_item).get_primary_value(first_item)

    # Get the primary value (name) from the first item in the dropdown and assert that the actual value matches the expected value
    expected_name = address_autofill_data.name
    assert expected_name == actual_value, (
        f"Expected {expected_name}, but got {actual_value}"
    )

    # Double-click inside Name field and hover the mouse over any saved address entry in the dropdown (without selecting it).
    address_autofill.double_click("form-field", labels=["organization"])
    # Get the first element from the autocomplete dropdown
    first_item = autofill_popup.get_nth_element(1)
    actual_value = autofill_popup.hover(first_item).get_primary_value(first_item)

    # Get the primary value (org) from the first item in the dropdown and assert that the actual value matches the expected value
    expected_org = address_autofill_data.organization
    assert expected_org == actual_value, (
        f"Expected {expected_org}, but got {actual_value}"
    )

    fields_to_test = [
        "name",
        "organization"
    ]

    for field in fields_to_test:
        address_autofill.verify_autofill_preview(field, )
