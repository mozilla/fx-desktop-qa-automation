from modules.browser_object import CreditCardPopup
from modules.page_object_autofill import Autofill
from modules.util import BrowserActions, CreditCardBase


class CreditCardFill(Autofill):
    """
    Page Object Model for auto site (https://mozilla.github.io/form-fill-examples/basic_cc.html)
    """

    URL_TEMPLATE = "https://mozilla.github.io/form-fill-examples/basic_cc.html"

    def fill_credit_card_info(self, info: CreditCardBase):
        fields = {
            "cc-name": info.name,
            "cc-number": info.card_number,
            "cc-exp-month": info.expiration_month,
            "cc-exp-year": info.expiration_year,
            "cc-csc": info.cvv,
        }
        ba = BrowserActions(self.driver)
        for field, value in fields.items():
            if value is not None:
                self.fill_input_element(ba, field, value)

        self.click_form_button("submit")

    def verify_all_fields(self, ccp: CreditCardPopup):
        fields = ["cc-name", "cc-number", "cc-exp-month", "cc-exp-year"]
        for field in fields:
            self.double_click("form-field", field)
            ccp.verify_popup()
