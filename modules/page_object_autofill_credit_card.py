from typing import List

from modules.browser_object import CreditCardPopup
from modules.classes.credit_card import CreditCardBase
from modules.page_object import Autofill
from modules.util import BrowserActions

class CreditCardFill(Autofill):
    """
    Page Object Model for auto site (https://mozilla.github.io/form-fill-examples/basic_cc.html)
    """

    URL_TEMPLATE = "https://mozilla.github.io/form-fill-examples/basic_cc.html"
    fields = ["cc-name", "cc-number", "cc-exp-month", "cc-exp-year"]

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
        for field in self.fields:
            self.double_click("form-field", field)
            ccp.verify_popup()

    def extract_credit_card_obj_into_list(
        self, credit_card_sample_data: CreditCardBase
    ) -> List[str]:
        """
        Extracts the credit card information from the object and returns it as a list.

        Attributes
        ----------
        credit_card_sample_data: CreditCardBase
            The credit card information object
        """
        ret_val = [
            credit_card_sample_data.name,
            credit_card_sample_data.card_number,
            credit_card_sample_data.expiration_month,
            f"20{credit_card_sample_data.expiration_year}",
        ]
        return ret_val

    def verify_four_fields(
        self, ccp: CreditCardPopup, credit_card_sample_data: CreditCardBase
    ):
        """
        Veriies that after clicking the autofill panel the information is filled correctly.

        Attributes
        ----------

        ccp: CreditCardPopup
            The credit card popup object

        credit_card_sample_data: CreditCardBase
            The object that contains all of the relevant information about the credit card autofill
        """
        self.double_click("form-field", "cc-name")
        with self.driver.context(self.driver.CONTEXT_CHROME):
            ccp.get_element("autofill-profile-option").click()

        info_list = self.extract_credit_card_obj_into_list(credit_card_sample_data)
        for i in range(len(info_list)):
            input_field = self.get_element("form-field", self.fields[i])
            assert info_list[i] == input_field.get_attribute("value")
