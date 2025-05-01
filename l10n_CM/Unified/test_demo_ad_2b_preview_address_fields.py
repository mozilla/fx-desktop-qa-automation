import pytest
from selenium.webdriver import Firefox

from modules.classes.autofill_base import AutofillAddressBase
from modules.page_object_autofill import AddressFill
from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "2888562"


@pytest.fixture()
def add_to_prefs_list(region: str):
    return [
        ("extensions.formautofill.creditCards.supportedCountries", region),
        ("extensions.formautofill.addresses.supported", "on"),
    ]


def test_hover_address_is_previewed(
    driver: Firefox,
    region: str,
    about_prefs_privacy: AboutPrefs,
    address_autofill: AddressFill,
    fill_and_save_address: AutofillAddressBase,
):
    """
    C2888562: Verify that hovering over address fields will preview all fields
    """
    # Create fake data
    address_autofill.open()

    # scroll to first form field
    address_autofill.scroll_to_form_field()

    # created fake data
    autofill_data = fill_and_save_address

    # Hover over each field and check data preview
    fields_to_test = [
        "street_address",
        "address_level_2",
        "address_level_1",
        "postal_code",
        "country_code",
    ]
    for field in fields_to_test:
        address_autofill.check_autofill_preview_for_field(field, autofill_data, region)
