import logging
from time import sleep

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC

from modules.classes.autofill_base import AutofillAddressBase
from modules.page_base import BasePage
from modules.util import BrowserActions


class AutofillSaveInfo(BasePage):
    """
    Page Object Model for auto site (https://mozilla.github.io/form-fill-examples/basic.html)
    """

    URL_TEMPLATE = "https://mozilla.github.io/form-fill-examples/basic.html"

    def save_information_basic(self, autofill_info: AutofillAddressBase):
        """
        Saves information passed in, in the form of an AutofillAddressBase object.
        Instantiates a dictionary of fields and fills in the input, if the input is not None.

        ...
        Attributes
        ---------

        autofill_info: AutofillAddressBase
        """
        ba = BrowserActions(self.driver)
        fields = {
            "name": autofill_info.name,
            "organization": autofill_info.organization,
            "street-address": autofill_info.street_address,
            "address-level2": autofill_info.address_level_2,
            "address-level1": autofill_info.address_level_1,
            "postal-code": autofill_info.postal_code,
            "country": autofill_info.country,
            "email": autofill_info.email,
            "tel": autofill_info.telephone,
        }

        for field, value in fields.items():
            if value is not None:
                self.fill_input_element(ba, field, value)

        self.click_form_button("submit")
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.get_element("doorhanger-save-button").click()

    def fill_input_element(self, ba: BrowserActions, field_name: str, term: str):
        """
        Given BrowserActions object, the string of the element to be identified and the string term to be sent to the input,
        identify the webelement and send the term to the input field without any additional keystrokes.

        ...
        Attributes
        ----------
        ba : BrowserActions
        field_name : str
            The name of the input field to be identified
        term: str
            The string to be sent to the input field
        """
        web_elem = self.get_element("form-field", field_name)
        ba.clear_and_fill_no_additional_keystroke(web_elem, term)

    def click_form_button(self, field_name):
        self.get_element("submit-button", field_name).click()

    def double_click_name_and_verify(self):
        """
        Double clicks the form field of Name and verifies that the autofill popup
        does NOT appear.
        """
        self.double_click("form-field", "name")
        with self.driver.context(self.driver.CONTEXT_CHROME):
            element = self.get_element("autofill-panel")
            try:
                self.expect(EC.element_to_be_clickable(element))
            except TimeoutException:
                logging.info("Autofill panel could not be clicked.")
