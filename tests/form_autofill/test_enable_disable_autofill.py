
import pytest
from selenium.webdriver import Firefox

from modules.autofill_object import AutofillSaveInfo
from modules.browser_object import Navigation
from modules.page_object import AboutPrefs

countries = ["CA", "US"]


@pytest.mark.parametrize("country_code", countries)
def test_enable_disable_autofill(driver: Firefox, country_code: str):
    """
    C122347, tests that after filling autofill and disabling it in settings that
    the autofill popups do not appear.
    """
    Navigation(driver).open()
    afsi = AutofillSaveInfo(driver).open()
    autofill_sample_data_canadian = afsi.fake_autofill_data(country_code)
    afsi.save_information_basic(autofill_sample_data_canadian)
    about_prefs = AboutPrefs(driver, category="privacy").open()
    about_prefs.find_setting_and_click("save-and-fill-addresses")
    new_afsi = AutofillSaveInfo(driver).open()
    new_afsi.double_click_name_and_verify()
