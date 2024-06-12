from selenium.webdriver.support import expected_conditions as EC

from modules.page_object import Autofill
from modules.util import AutofillAddressBase, BrowserActions


class AddressFill(Autofill):
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

        web_elem = self.get_element("form-field", labels=[field_name])
        ba.clear_and_fill(web_elem, term, press_enter=False)

    def click_form_button(self, field_name: str):
        self.get_element("submit-button", labels=[field_name]).click()

    def click(self, name: str, label: str) -> Autofill:
        elem = self.get_element(name, labels=[label])
        self.actions.click(elem).perform()
        return self

    def click_address(self) -> Autofill:
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.get_element("select-address").click()
        return self

    def click_clear(self) -> Autofill:
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.get_element("clear-address").click()
        return self

    def verify_autofill_displayed(self):
        """
        Verifies that the autofill suggestions are displayed.
        """
        with self.driver.context(self.driver.CONTEXT_CHROME):
            element = self.get_element("select-address")
            self.expect(EC.visibility_of(element))

    def double_click(self, name: str, labels: list[str]):
        """
        Double-click on the specified element.

        Parameters:
        name (str): The name of the element to double-click.
        labels (list[str]): Additional labels to identify the element (optional).
        """
        elem = self.get_element(name, labels=labels)
        self.actions.double_click(elem).perform()
