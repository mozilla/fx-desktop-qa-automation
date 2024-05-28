from selenium.webdriver import Firefox

from modules.browser_object import CreditCardPopup, Navigation
from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object import AboutPrefs

# from modules.page_object import AboutPrefs
from modules.page_object_autofill_credit_card import CreditCardFill
from modules.util import BrowserActions, Utilities


def test_autofill_update_credit_card(driver: Firefox):
    """
    C122406, updates the name of the credit card holder and ensure no new profile is created and data is saved correctly
    """
    nav = Navigation(driver)
    util = Utilities()

    nav.open()
    credit_card_fill_obj = CreditCardFill(driver).open()
    autofill_popup_obj = AutofillPopup(driver)
    credit_card_popoup_obj = CreditCardPopup(driver)
    browser_action_obj = BrowserActions(driver)

    credit_card_sample_data = util.fake_credit_card_data()
    credit_card_fill_obj.fill_credit_card_info(credit_card_sample_data)
    autofill_popup_obj.press_doorhanger_save()
    credit_card_fill_obj.press_autofill_panel(credit_card_popoup_obj)

    # updating the name of the cc
    new_cc_name = util.fake_credit_card_data().name
    credit_card_sample_data.name = new_cc_name

    credit_card_fill_obj.verify_updated_information(
        credit_card_popoup_obj,
        autofill_popup_obj,
        credit_card_sample_data,
        "cc-name",
        credit_card_sample_data.name,
    )

    # navigate to settings
    about_prefs = AboutPrefs(driver, category="privacy").open()
    about_prefs.get_element("prefs-button", labels=["Saved payment methods"]).click()

    iframe = about_prefs.get_element("browser-popup")
    browser_action_obj.switch_to_iframe_context(iframe)

    element = about_prefs.get_element("cc-saved-options", multiple=True)
    assert len(element) == 1

    print(element.get_dom_attribute("data-l10n-args"))
    print(credit_card_sample_data)
    browser_action_obj.switch_to_content_context()

    # new_cc_number = util.fake_credit_card_data().card_number
    # credit_card_sample_data.card_number = new_cc_number

    # credit_card_fill_obj.verify_updated_information(credit_card_popoup_obj,
    #                                                 autofill_popup_obj,
    #                                                 credit_card_sample_data,
    #                                                 "cc-number",
    #                                                 credit_card_sample_data.card_number)
