from typing import Union

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

    def ensure_autofill_dropdown_not_visible(self):
        """Verifies that the autofill dropdown does NOT appear"""
        self.element_not_visible("select-form-option")
        return self

    def ensure_autofill_dropdown_visible(self):
        """Verifies that the autofill dropdown appears"""
        self.element_visible("select-form-option")
        return self

    # Interaction with popup elements
    def click_doorhanger_button(self, button_type: str) -> BasePage:
        """Presses a button in the doorhanger popup (e.g., save, update, dropdown)"""
        self.element_visible(f"doorhanger-{button_type}-button")
        self.click_on(f"doorhanger-{button_type}-button")
        return self

    # Interaction with form options
    def click_autofill_form_option(self) -> BasePage:
        """Clicks the credit card or address selection in the autofill panel"""
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.get_element("select-form-option").click()
        return self

    def click_clear_form_option(self) -> BasePage:
        """Clicks to clear the saved form option (address or credit card)"""
        self.click_on("clear-form-option")
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
