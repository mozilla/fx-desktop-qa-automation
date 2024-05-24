from time import sleep

from selenium.webdriver import Firefox

from modules.browser_object import CreditCardPopup, Navigation
from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object import AboutPrefs
from modules.page_object_autofill_credit_card import CreditCardFill
from modules.util import BrowserActions, Utilities


def test_autofill_update_credit_card(driver: Firefox):
    nav = Navigation(driver)
    util = Utilities()
    ba = BrowserActions(driver)

    nav.open()
    credit_card_fill_obj = CreditCardFill(driver).open()
    autofill_popup_obj = AutofillPopup(driver)
    credit_card_popoup_obj = CreditCardPopup(driver)

    credit_card_fill_obj.fake_and_fill(util, autofill_popup_obj)

    new_credit_card_data = util.fake_credit_card_data()

    # change name

    credit_card_fill_obj.update_credit_card_information(
        credit_card_popoup_obj, autofill_popup_obj, "cc-name", new_credit_card_data.name
    )
    # util.write_html_content("file", driver, True)
    sleep(5)
