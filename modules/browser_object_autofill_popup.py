from typing import List, Union

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

from modules.page_base import BasePage


class AutofillPopup(BasePage):
    """
    Page Object Model for the popups that have to do with autofill (related to credit card and addresses)
    """

    URL_TEMPLATE = ""
    iframe = None

    # Verification methods
    def verify_autofill_displayed(self):
        """Confirms that autofill popup has loaded"""
        self.element_clickable("autofill-panel")

    def verify_element_displayed(self, reference: Union[str, tuple, WebElement]):
        """Confirms that an element exists in popup"""
        self.element_clickable(reference)

    def verify_no_popup_panel(self):
        """Verifies that the autofill popup does NOT appear"""
        with self.driver.context(self.driver.CONTEXT_CHROME):
            element = self.get_element("autofill-panel")
            self.expect_not(EC.element_to_be_clickable(element))

    def verify_popup(self):
        """Verifies that the autofill popup is clickable"""
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.expect(
                EC.element_to_be_clickable(self.get_element("autofill-cc-panel"))
            )

    # Interaction with popup elements
    def click_doorhanger_button(self, button_type: str) -> BasePage:
        """Presses a button in the doorhanger popup (e.g., save, update, dropdown)"""
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.get_element(f"doorhanger-{button_type}-button").click()
        return self

    # Interaction with form options
    def click_autofill_form_option(self) -> BasePage:
        """Clicks the credit card or address selection in the autofill panel"""
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.get_element("select-form-option").click()
        return self

    def click_clear_form_option(self) -> BasePage:
        """Clicks to clear the saved form option (address or credit card)"""
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.get_element("clear-form-option").click()
        return self

    # Interaction with autocomplete list elements
    def get_nth_element(self, index: str) -> WebElement:
        """
        Get the nth element from the autocomplete list
        Parameters: index (str): The index of the element to retrieve (1-based)
        Returns: WebElement: The nth element in the autocomplete list
        """
        with self.driver.context(self.driver.CONTEXT_CHROME):
            return self.wait.until(
                EC.visibility_of_element_located(
                    (
                        "css selector",
                        f".autocomplete-richlistbox .autocomplete-richlistitem:nth-child({index})",
                    )
                )
            )

    def get_primary_value(self, element: WebElement) -> str:
        """
        Get the primary value from the autocomplete element
        Parameters: element (WebElement): The autocomplete element from which to retrieve the primary value
        Returns: str: The primary value extracted from the element's attribute
        """
        with self.driver.context(self.driver.CONTEXT_CHROME):
            return element.get_attribute("ac-value")

    # Interaction with about:preferences modals
    def get_all_saved_cc_profiles(self) -> List[WebElement]:
        """Gets the saved credit card profiles in the cc panel"""
        if self.iframe:
            with self.driver.switch_to.frame(self.iframe):
                return self.get_element("cc-saved-options", multiple=True)
        else:
            return self.get_element("cc-saved-options", multiple=True)

    def click_popup_panel_button(self, field: str) -> BasePage:
        """Clicks the popup panel button for the specified field"""
        if self.iframe:
            with self.driver.switch_to.frame(self.iframe):
                self.get_element("cc-popup-button", labels=[field]).click()
        else:
            self.get_element("cc-popup-button", labels=[field]).click()
        return self
