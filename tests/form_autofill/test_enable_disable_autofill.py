import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation
from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object import AboutPrefs
from modules.page_object_autofill import AddressFill
from modules.util import Utilities

COUNTRY_CODE = "US"


@pytest.fixture()
def test_case():
    return "122347"


def test_enable_disable_autofill(driver: Firefox):
    """
    C122347, tests that after filling autofill and disabling it in settings that
    the autofill popups do not appear.
    """
    # instantiate objects
    Navigation(driver)
    af = AddressFill(driver).open()
    afp = AutofillPopup(driver)
    util = Utilities()

    # create fake data, fill it in and press submit and save on the doorhanger
    autofill_sample_data = util.fake_autofill_data(COUNTRY_CODE)
    af.save_information_basic(autofill_sample_data)
    afp.click_doorhanger_button("save")
    about_prefs = AboutPrefs(driver, category="privacy").open()
    about_prefs.get_element("save-and-fill-addresses").click()

    # creating new objects to prevent stale webelements
    new_af = AddressFill(driver).open()
    new_afp = AutofillPopup(driver)

    # verifying the popup panel does not appear
    new_af.double_click("form-field", labels=["name"])
    new_afp.ensure_autofill_dropdown_not_visible()
