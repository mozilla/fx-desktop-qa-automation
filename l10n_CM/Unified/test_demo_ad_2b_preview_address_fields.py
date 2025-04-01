import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object_autofill import AddressFill
from modules.page_object_prefs import AboutPrefs
from modules.util import Utilities


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
    autofill_popup: AutofillPopup,
    util: Utilities,
):
    """
    C2888562: Verify that hovering over address fields will preview all fields
    """
    # Create fake data and fill it in
    address_autofill.open()
    autofill_data = address_autofill.fill_and_save(util, autofill_popup)

    # Hover over each field and check data preview
    fields_to_test = [
        "street-address",
        "address-level2",  # city
        "address-level1",  # state/province
        "postal-code",
        "country",
    ]
    for field in fields_to_test:
        address_autofill.check_autofill_preview_for_field(
            field, autofill_data, autofill_popup, util
        )
