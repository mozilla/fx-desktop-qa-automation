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
    address_values = {str(val) for val in address_autofill_data.__dict__.values()}
    about_prefs_privacy.open_and_switch_to_saved_addresses_popup()

    # verify that the address saved is the same.
    elements = about_prefs_privacy.get_element("saved-addresses-values").text.split(",")
    total_address_match = True
    for element in elements:
        sanitized_element = data_sanitizer(
            util, element, region, inverted_state_province_abbr
        )
        # temporary fix until Italian province mappings are added.
        if (
            len(sanitized_element) == 2
            and sanitized_element != region
            and region not in ["US", "CA"]
        ):
            continue
        address_match = False
        for val in address_values:
            if sanitized_element in val:
                address_match = True
                break
        total_address_match = total_address_match and address_match
    assert total_address_match, "Address found is not equal to address created!"


def data_sanitizer(util: Utilities, value: str, region: str, state_province: Dict):
    value = value.strip()
    if value[0] == "+":
        return util.normalize_regional_phone_numbers(value, region)
    elif len(value) == 2 and value != region:
        return state_province.get(value, value)
    return value
