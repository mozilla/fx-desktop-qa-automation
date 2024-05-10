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
    """
    C122347, tests that after filling autofill and disabling it in settings that
    the autofill popups do not appear.
    """
    Navigation(driver).open()
    afsi = AutofillSaveInfo(driver).open()
    afsi.save_information_basic(autofill_sample_data_canadian)
    about_prefs = AboutPrefs(driver, category="privacy").open()
    about_prefs.find_setting_and_click("save-and-fill-addresses")
    new_afsi = AutofillSaveInfo(driver).open()
    new_afsi.double_click_name_and_verify()
