from typing import List

from modules.browser_object import CreditCardPopup
from modules.browser_object_autofill_popup import AutofillPopup
from modules.classes.credit_card import CreditCardBase
from modules.page_object_autofill import Autofill
from modules.util import BrowserActions, Utilities
from selenium.webdriver.support import expected_conditions as EC


class CreditCardFill(Autofill):
    """
    Page Object Model for auto site (https://mozilla.github.io/form-fill-examples/basic_cc.html)
    """

    URL_TEMPLATE = "https://mozilla.github.io/form-fill-examples/basic_cc.html"
    fields = ["cc-name", "cc-number", "cc-exp-month", "cc-exp-year"]

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
        for field in self.fields:
            self.double_click("form-field", field)
            ccp.verify_popup()

    def verify_four_fields(
        self, ccp: CreditCardPopup, credit_card_sample_data: CreditCardBase
    ) -> Autofill:
        """
        Verifies that after clicking the autofill panel the information is filled correctly.

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
            input_field = self.get_element("form-field", labels=[self.fields[i]])
            assert info_list[i] == input_field.get_attribute("value")
        return self

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

    def update_field(
        self, field: str, field_data: str, autofill_popup_obj: AutofillPopup
    ):
        ba = BrowserActions(self.driver)
        self.fill_input_element(ba, field, field_data)
        autofill_popup_obj.press_doorhanger_save()

    def press_autofill_panel(self, credit_card_popoup_obj: CreditCardPopup):
        """
        Presses the autofill panel that pops up after you double click an input field
        """
        self.double_click("form-field", "cc-name")
        with self.driver.context(self.driver.CONTEXT_CHROME):
            credit_card_popoup_obj.get_element("autofill-profile-option").click()

    def update_credit_card_information(
        self,
        credit_card_popoup_obj: CreditCardPopup,
        autofill_popup_obj: AutofillPopup,
        field_name: str,
        field_data: str,
        save_card=False,
    ):
        """
        Updates the credit card based on field that is to be changed by first autofilling everything then updating the field of choice then pressing submit and handling the popup.
        """
        self.press_autofill_panel(credit_card_popoup_obj)
        self.update_field(field_name, field_data, autofill_popup_obj)
        self.click_form_button("submit")

        with self.driver.context(self.driver.CONTEXT_CHROME):
            if not save_card:
                credit_card_popoup_obj.get_element(
                    "update-card-info-popup-button"
                ).click()
            else:
                autofill_popup_obj.get_element("doorhanger-save-button").click()

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

    def verify_updated_information(
        self,
        credit_card_popoup_obj: CreditCardPopup,
        autofill_popup_obj: AutofillPopup,
        credit_card_sample_data: CreditCardBase,
        field_name: str,
        new_data: str,
    ) -> Autofill:
        """
        Verfies that there is only 1 profile in the popup panel, updates the credit card information and verifies all the fields
        according to the passed in credit card information object

        Attributes
        ----------

        credit_card_popoup_obj: CreditCardPopup
            The credit card popup object

        autofill_popup_obj: AutofillPopup
            An instance of autofill popup object

        credit_card_sample_data: CreditCardBase
            An instance of the fake generated data

        field_name: str
            The name of the field to update

        new_data: str
            The data to update the field with
        """

        # updating the profile accordingly
        self.update_credit_card_information(
            credit_card_popoup_obj, autofill_popup_obj, field_name, new_data
        )

        # verifiyng the correct data
        self.verify_four_fields(credit_card_popoup_obj, credit_card_sample_data)
        return self

    def update_cc_name(
        self,
        util: Utilities,
        credit_card_sample_data: CreditCardBase,
        autofill_popup_obj: AutofillPopup,
        credit_card_popoup_obj: CreditCardPopup,
    ) -> Autofill:
        """
        Generates a new name, updates the credit card information in the form.
        """
        new_cc_name = util.fake_credit_card_data().name
        credit_card_sample_data.name = new_cc_name

        self.verify_updated_information(
            credit_card_popoup_obj,
            autofill_popup_obj,
            credit_card_sample_data,
            "cc-name",
            credit_card_sample_data.name,
        )
        return self

    def update_cc_exp_month(
        self,
        util: Utilities,
        credit_card_sample_data: CreditCardBase,
        autofill_popup_obj: AutofillPopup,
        credit_card_popoup_obj: CreditCardPopup,
    ) -> Autofill:
        """
        Generates a new expiry month, updates the credit card information in the form.
        """
        new_cc_exp_month = util.fake_credit_card_data().expiration_month
        credit_card_sample_data.expiration_month = new_cc_exp_month

        self.verify_updated_information(
            credit_card_popoup_obj,
            autofill_popup_obj,
            credit_card_sample_data,
            "cc-exp-month",
            credit_card_sample_data.expiration_month,
        )
        return self

    def update_cc_exp_year(
        self,
        util: Utilities,
        credit_card_sample_data: CreditCardBase,
        autofill_popup_obj: AutofillPopup,
        credit_card_popoup_obj: CreditCardPopup,
    ) -> Autofill:
        """
        Generates a new expiry year, updates the credit card information in the form.
        """
        new_cc_exp_year = util.fake_credit_card_data().expiration_year
        credit_card_sample_data.expiration_year = new_cc_exp_year

        self.verify_updated_information(
            credit_card_popoup_obj,
            autofill_popup_obj,
            credit_card_sample_data,
            "cc-exp-year",
            credit_card_sample_data.expiration_year,
        )
        return self

    def click_credit_card(self):
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.get_element("select-form-option").click()
        return self

    def click_clear(self):
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.get_element("clear-creditcard").click()
        return self

    def verify_autofill_displayed(self):
        """
        Verifies that the autofill suggestions are displayed.
        """
        with self.driver.context(self.driver.CONTEXT_CHROME):
            element = self.get_element("select-form-option")
            self.expect(EC.visibility_of(element))
