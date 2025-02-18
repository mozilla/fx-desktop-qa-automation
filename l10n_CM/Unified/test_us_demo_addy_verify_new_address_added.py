from typing import Dict

import pytest
from selenium.webdriver import Firefox

from modules.page_object_prefs import AboutPrefs
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "2886580"


@pytest.fixture()
def region():
    return "US"


@pytest.fixture()
def add_prefs(region: str):
    return [
        ("browser.search.region", region),
        ("extensions.formautofill.creditCards.supportedCountries", region),
        ("extensions.formautofill.addresses.supported", "on"),
    ]


def test_verify_new_address_is_added(
    driver: Firefox, region: str, about_prefs: AboutPrefs, util: Utilities
):
    """
    C2886580: Verify that a new Address can be added
    """
    # invert state_province_abbr to help with verification
    inverted_state_province_abbr = {v: k for k, v in util.state_province_abbr.items()}
    # generate fake data for region
    address_autofill_data = util.fake_autofill_data(region)

    # open saved addresses and add entry
    about_prefs.open()
    about_prefs.add_entry_to_saved_addresses(address_autofill_data)

    # verify that the address saved is the same.
    # The address saved in step 2 is listed in the "Saved addresses" modal: name and organization
    elements = about_prefs.get_element("saved-addresses-values").text.split(",")
    address_match = all(
        data_sanitizer(element, region, inverted_state_province_abbr)
        in address_autofill_data.__dict__.values()
        for element in elements
    )
    assert address_match, "Address found is not equal to address created!"


def data_sanitizer(value: str, region: str, state_province: Dict):
    value = value.strip()
    if value[0] == "+":
        return value[1:]
    elif len(value) == 2 and value != region:
        return state_province.get(value, value)
    return value
