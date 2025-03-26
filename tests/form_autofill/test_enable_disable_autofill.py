import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation
from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object import AboutPrefs
from modules.page_object_autofill import AddressFill
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "122347"


def test_enable_disable_autofill(
    driver: Firefox,
    about_prefs_privacy: AboutPrefs,
    address_autofill: AddressFill,
    autofill_popup: AutofillPopup,
    util: Utilities,
    region: str,
):
    """
    C122347, tests that after filling autofill and disabling it in settings that
    the autofill popups do not appear.

    Arguments:
        about_prefs_privacy: AboutPrefs instance (privacy category)
        autofill_popup: AutofillPopup instance
        util: Utilities instance
    """
    address_autofill.open()

    # create fake data, fill it in and press submit and save on the doorhanger
    autofill_sample_data = util.fake_autofill_data(region)
    address_autofill.save_information_basic(autofill_sample_data)
    autofill_popup.click_doorhanger_button("save")

    about_prefs_privacy.open()
    about_prefs_privacy.get_element("save-and-fill-addresses").click()

    address_autofill.open()

    # verifying the popup panel does not appear
    address_autofill.double_click("form-field", labels=["name"])
    autofill_popup.ensure_autofill_dropdown_not_visible()
