from selenium.webdriver.support import expected_conditions as EC

from modules.browser_object import CreditCardPopup
from modules.browser_object_autofill_popup import AutofillPopup
from modules.page_object_autofill import Autofill
from modules.util import BrowserActions, CreditCardBase, Utilities


class CreditCardFill(Autofill):
    """
    Page Object Model for auto site (https://mozilla.github.io/form-fill-examples/basic_cc.html)
    """

    URL_TEMPLATE = "https://mozilla.github.io/form-fill-examples/basic_cc.html"

    def fill_credit_card_info(self, info: CreditCardBase):
        """
        Fills a credit card form with the provided information.

        ...

        Attributes
        ----------

        info:  CreditCardBase
            An instance of the CreditCardBase class containing the credit card details.

        """
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
        """
        Verifies the pre-filled values in the credit card form.

        ...

        Attributes
        ----------

        ccp: CreditCardPopup
            An instance of the CreditCardPopup class used to interact with the verification popup.
        """
        fields = ["cc-name", "cc-number", "cc-exp-month", "cc-exp-year"]
        for field in fields:
            self.double_click("form-field", field)
            ccp.verify_popup()

    def fake_and_fill(self, util: Utilities, autofill_popup_obj: AutofillPopup):
        """
        Fills a credit card form with randomly generated data and interacts with the autofill popup.

        ...

        Attributes
        ----------
            util: Utilities
                An instance of the Utilities class
            autofill_popup_obj: AutofillPopup
                An instance of the AutofillPopup class used to interact with the autofill popup
        """
        credit_card_sample_data = util.fake_credit_card_data()
        self.fill_credit_card_info(credit_card_sample_data)
        autofill_popup_obj.press_doorhanger_save()
