from modules.page_base import BasePage
from modules.util import BrowserActions


class Autofill(BasePage):
    """
    Page Object Model for auto site (https://mozilla.github.io/form-fill-examples/) base parent object of all autofill page related objects
    """

    URL_TEMPLATE = "https://mozilla.github.io/form-fill-examples/"

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
        form_field_element = self.get_element("form-field", labels=[field_name])
        ba.clear_and_fill(form_field_element, term, press_enter=False)

    def click_form_button(self, field_name):
        self.get_element("submit-button", labels=[field_name]).click()
