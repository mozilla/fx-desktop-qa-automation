import pytest
from selenium.webdriver import Firefox

from modules.classes.autofill_base import AutofillAddressBase
from modules.page_object_autofill import AddressFill


@pytest.fixture()
def test_case():
    return "2888557"


def test_demo_ad_hover_name_org(
    driver: Firefox,
    region: str,
    address_autofill: AddressFill,
    fill_and_save_address: AutofillAddressBase,
):
    """
    C2888557 - Verify Autofill Preview on hover over dropdown entries for name/org fields
    """
    # Create fake data
    address_autofill.open()

    # scroll to first form field
    address_autofill.scroll_to_form_field()

    # created fake data
    autofill_data = fill_and_save_address

    # Hover over each field and check data preview
    fields_to_test = ["name", "given_name", "family_name", "organization"]
    for field in fields_to_test:
        address_autofill.check_autofill_preview_for_field(field, autofill_data, region)
