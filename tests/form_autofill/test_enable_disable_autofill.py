import pytest
from selenium.webdriver import Firefox

from modules.autofill_object import AddressFill
from modules.browser_object_autofill_popup import AutofillPopup
from modules.browser_object import Navigation
from modules.page_object import AboutPrefs
from modules.util import Utilities

countries = ["CA", "US"]


@pytest.mark.parametrize("country_code", countries)
def test_enable_disable_autofill(driver: Firefox, country_code: str):
    """
    C122347, tests that after filling autofill and disabling it in settings that
    the autofill popups do not appear.
    """
    # instantiate objects
    Navigation(driver).open()
    af = AddressFill(driver).open()
    afp = AutofillPopup(driver)
    util = Utilities()

    # create fake data, fill it in and press submit and save on the doorhanger
    autofill_sample_data = util.fake_autofill_data(country_code)
    af.save_information_basic(autofill_sample_data)
    afp.press_doorhanger_save()
    about_prefs = AboutPrefs(driver, category="privacy").open()
    about_prefs.get_element("save-and-fill-addresses").click()

    # creating new objects to prevent stale webelements
    new_af = AddressFill(driver).open()
    new_afp = AutofillPopup(driver)

    # verifying the popup panel does not appear
    new_af.double_click("form-field", "name")
    new_afp.verify_no_popup_panel()
