from time import sleep

from selenium.webdriver import Firefox

from modules.autofill_object import AutofillSaveInfo
from modules.browser_object import Navigation
from modules.classes.autofill_base import AutofillAddressBase
from modules.page_object import AboutPrefs

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
    nav = Navigation(driver).open()
    afsi = AutofillSaveInfo(driver).open()
    afsi.save_information_basic(autofill_sample_data_canadian)
    # press save on the top browser thing NOTE DONT KNOW HOW TO DO

    # navigate to about:preferences
    aboout_prefs = AboutPrefs(driver, category="privacy").open()
    # # disable autofill NOTE DOES NOT WORK
    aboout_prefs.find_setting_and_click("save-and-fill-addresses")
    # go back to https://mozilla.github.io/form-fill-examples/basic.html?
    # afsi.open()
    # double click name

    # ensure nothing pops up
