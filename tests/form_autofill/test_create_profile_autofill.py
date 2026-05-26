import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutPrefs
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "122348"


def test_create_address_profile(
    driver: Firefox, about_prefs_addresses: AboutPrefs, util: Utilities, region: str
):
    """
    C122348, creating an address profile

    Arguments:
        about_prefs_privacy: AboutPrefs instance (privacy category)
        util: Utilities instance
        region: country code in use
    """
    about_prefs_addresses.open()

    # create sample data
    autofill_sample_data = util.fake_autofill_data(region)

    # add entry to saved addresses
    about_prefs_addresses.add_entry_to_saved_addresses(autofill_sample_data)

    saved_address_data = about_prefs_addresses.get_data_from_saved_address()

    autofilled_dict = vars(autofill_sample_data)
    state_provs = util.state_province_abbr
    for element in autofilled_dict.keys():
        if "name" in element:
            assert autofilled_dict[element] in saved_address_data.get("name")
        elif "address" in element or "postal_code" in element:
            if autofilled_dict[element] in state_provs:
                addr_line_value = state_provs[autofilled_dict[element]]
            else:
                addr_line_value = autofilled_dict[element]
            assert addr_line_value in saved_address_data.get("address")
