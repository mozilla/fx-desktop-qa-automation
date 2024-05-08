from modules.classes.autofill_base import AutofillAddressBase
from modules.page_base import BasePage
from modules.util import BrowserActions


class AutofillSaveInfo(BasePage):
    """
    Page Object Model for auto site (https://mozilla.github.io/form-fill-examples/basic.html)
    """

    def save_information_basic(self, autofill_info: AutofillAddressBase):
        ba = BrowserActions(self.driver)
        self.fill_input_element(ba, "organization-field", "hello")
        pass

    def fill_input_element(
        self, ba: BrowserActions, element_idenitifer: str, term: str
    ):
        """
        Given BrowserActions object, the string of the element to be identified and the string term to be sent to the input,
        identify the webelement and send the term to the input field without any additional keystrokes.

        ...

        Parameters
        ----------
        ba : BrowserActions
        element_idenitifer : str
            The identified for the element to have input sent to
        term: str
            The string to be sent to the input field
        """
        self.get_element(element_idenitifer)
