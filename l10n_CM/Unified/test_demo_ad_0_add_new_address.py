from typing import Dict

import pytest
from selenium.webdriver import Firefox

from modules.classes.autofill_base import AutofillAddressBase
from modules.page_object_prefs import AboutPrefs
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "2886580"


@pytest.fixture()
def add_to_prefs_list(region: str):
    return [
        ("extensions.formautofill.creditCards.supportedCountries", region),
        ("extensions.formautofill.addresses.supported", "on"),
    ]


def test_verify_new_address_is_added(
    driver: Firefox,
    region: str,
    about_prefs_privacy: AboutPrefs,
    util: Utilities,
    populate_saved_addresses: AutofillAddressBase,
):
    """
    C2886580: Verify that a new Address can be added
    """
    # invert state_province_abbr to help with verification
    inverted_state_province_abbr = {v: k for k, v in util.state_province_abbr.items()}

    # address autofill data
    address_autofill_data = populate_saved_addresses
    about_prefs_privacy.open_and_switch_to_saved_addresses_popup()

    # verify that the address saved is the same.
    # The address saved in step 2 is listed in the "Saved addresses" modal: name and organization
    elements = about_prefs_privacy.get_element("saved-addresses-values").text.split(",")
    address_match = all(
        data_sanitizer(util, element, region, inverted_state_province_abbr)
        in address_autofill_data.__dict__.values()
        for element in elements
    )
    assert address_match, "Address found is not equal to address created!"


def data_sanitizer(util: Utilities, value: str, region: str, state_province: Dict):
    value = value.strip()
    if value[0] == "+":
        return util.normalize_regional_phone_numbers(value, region)
    elif len(value) == 2 and value != region:
        return state_province.get(value, value)
    return value
