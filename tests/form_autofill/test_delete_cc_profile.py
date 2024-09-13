import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation
from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object import AboutPrefs
from modules.page_object_autofill_credit_card import CreditCardFill
from modules.util import BrowserActions, Utilities


@pytest.fixture()
def test_case():
    return "122391"


@pytest.mark.unstable
def test_delete_cc_profile(driver: Firefox):
    """
    C122391, Ensuring that deleting cc profiles will make it so CC does not show up in the grid
    """
    # instantiate objects
    nav = Navigation(driver)
    util = Utilities()

    nav.open()
    credit_card_fill_obj = CreditCardFill(driver).open()
    autofill_popup_obj = AutofillPopup(driver)
    browser_action_obj = BrowserActions(driver)

    # create two profiles
    credit_card_sample_data = util.fake_credit_card_data()
    credit_card_fill_obj.fill_credit_card_info(credit_card_sample_data)
    autofill_popup_obj.click_doorhanger_button("save")

    credit_card_sample_data = util.fake_credit_card_data()
    credit_card_fill_obj.fill_credit_card_info(credit_card_sample_data)
    autofill_popup_obj.click_doorhanger_button("save")

    # navigate to prefs
    about_prefs = AboutPrefs(driver, category="privacy").open()
    iframe = about_prefs.get_saved_payments_popup_iframe()
    browser_action_obj.switch_to_iframe_context(iframe)

    # verify there are 2 profiles at first
    about_prefs_cc_popup = AutofillPopup(driver)
    cc_profiles = about_prefs_cc_popup.get_all_saved_cc_profiles()
    assert len(cc_profiles) == 2

    # delete a profile and verify there is only 1 left
    cc_profiles[0].click()
    about_prefs_cc_popup.click_popup_panel_button("autofill-manage-remove-button")
    cc_profiles = about_prefs_cc_popup.get_all_saved_cc_profiles()
    assert len(cc_profiles) == 1
