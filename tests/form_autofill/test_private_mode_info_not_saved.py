import pytest
from selenium.webdriver import Firefox

from modules.browser_object import AutofillPopup
from modules.page_object import (AddressFill, AboutPrefs)
from modules.util import (Utilities, BrowserActions)

@pytest.fixture()
def set_prefs():
    """Set prefs"""
    return [
        ("extensions.formautofill.creditCards.reauth.optout", False),
        ("extensions.formautofill.reauth.enabled", False),
        ("browser.privatebrowsing.autostart", True)
    ]

countries = ["CA", "US"]

@pytest.mark.parametrize("country_code", countries)
def test_private_mode_info_not_saved(driver: Firefox, country_code: str):
    address_form_fields = AddressFill(driver).open()
    autofill_popup = AutofillPopup(driver)
    util = Utilities()
    ba = BrowserActions(driver)


    # Create fake data, fill in the form, and press submit and save on the doorhanger
    autofill_sample_data = util.fake_autofill_data(country_code)
    address_form_fields.save_information_basic(autofill_sample_data)
    autofill_popup.verify_no_popup_panel()

    about_prefs = AboutPrefs(driver, category="privacy").open()

    iframe_address_popup = about_prefs.press_button_get_popup_dialog_iframe(
        "Saved addresses"
    )
    ba.switch_to_iframe_context(iframe_address_popup)
    about_prefs.element_does_not_exist("saved-addresses-values")
