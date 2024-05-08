from selenium.webdriver import Firefox

from modules.autofill_object import AutofillSaveInfo
from modules.browser_object import Navigation
from modules.classes.autofill_base import AutofillAddressBase

AUTOFILL_BASE_URL = "https://mozilla.github.io/form-fill-examples/basic.html?"

autofill_sample_data_canadian = AutofillAddressBase(
    name="John Doe",
    organization="Mozilla",
    street_address="1 Bloor Street",
    address_level_2="Toronto",
    address_level_1="ON",
    postal_code="M4B0A3",
    country="CA",
    email="Johndoe@hello.com",
    telephone="1234567890",
)


def test_enable_disable_autofill(driver: Firefox):
    afsi = AutofillSaveInfo(driver)
    nav = Navigation(driver).open()
    nav.search(AUTOFILL_BASE_URL)
    afsi.save_information_basic(autofill_sample_data_canadian)
    # go to prefs security and privacy
    # nav.search("")
    # disable autofill

    # go back to https://mozilla.github.io/form-fill-examples/basic.html?

    # double click name

    # ensure nothing pops up
