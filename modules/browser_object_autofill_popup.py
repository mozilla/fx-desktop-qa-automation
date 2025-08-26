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

    @BasePage.context_chrome
    def ensure_autofill_dropdown_not_visible(self):
        """
        Verifies that the autofill dropdown does not appear
        checks if the parent pop up component has hidden attribute.
        """
        self.element_exists("pop-up-component")
        popup_component = self.get_element("pop-up-component")
        if len(popup_component.get_attribute("innerHTML")) > 1:
            self.expect_element_attribute_contains(
                "pop-up-component-box", "style", "0px;"
            )
        else:
            self.expect_element_attribute_contains("pop-up-component", "hidden", "true")
        return self

    @BasePage.context_chrome
    def ensure_autofill_dropdown_visible(self):
        """
        Verifies that the autofill dropdown appears
        checks if the parent pop up component has hidden attribute.
        """
        self.element_clickable("pop-up-component-box")
        return self

    @BasePage.context_chrome
    def hover_over_autofill_panel(self):
        self.element_clickable("pop-up-component-box")
        self.hover("pop-up-component-box")
        return self

    # Interaction with popup elements
    def click_doorhanger_button(self, button_type: str) -> BasePage:
        """Presses a button in the doorhanger popup (e.g., save, update, dropdown)"""
        self.element_visible(f"doorhanger-{button_type}-button")
        self.click_on(f"doorhanger-{button_type}-button")
        return self

    # Interaction with form options
    @BasePage.context_chrome
    def click_autofill_form_option(self) -> BasePage:
        """Clicks the credit card or address selection in the autofill panel"""
        self.get_element("select-form-option").click()
        return self

    def click_clear_form_option(self) -> BasePage:
        """Clicks to clear the saved form option (address or credit card)"""
        self.click_on("clear-form-option")
        return self

    def get_doorhanger_cc_number(self) -> str:
        """Retrieves the last 4 digits of the credit card from the doorhanger popup"""
        return self.get_element("doorhanger-cc-number").text

    @BasePage.context_chrome
    def get_cc_doorhanger_data(self, selector: str) -> str:
        """
        get text for the credit card doorhanger data.
        """
        return self.get_element(selector).text

    # Interaction with autocomplete list elements
    @BasePage.context_chrome
    def get_nth_element(self, index: str | int) -> WebElement:
        """
        Get the nth element from the autocomplete list
        Parameters: index (str): The index of the element to retrieve (1-based)
        Returns: WebElement: The nth element in the autocomplete list
        """
        self.wait.until(
            EC.visibility_of(
                self.get_element("select-form-option-by-index", labels=[str(index)])
            )
        )
        return self.get_element("select-form-option-by-index", labels=[str(index)])

    @BasePage.context_chrome
    def select_nth_element(self, index: int):
        """
        Select the nth element from the autocomplete list
        Arguments:
            index (int): The index of the element to retrieve (1-based)
        """
        self.element_clickable("pop-up-component-box")
        self.click_on("select-form-option-by-index", labels=[str(index)])

    @BasePage.context_chrome
    def select_autofill_panel(self):
        """
        Select the first autofill panel in the autocomplete list.
        """
        self.element_clickable("select-form-option-autofill")
        self.click_on("select-form-option-autofill")
        return self

    @BasePage.context_chrome
    def get_primary_value(self, element: WebElement) -> str:
        """
        Get the primary value from the autocomplete element
        Parameters: element (WebElement): The autocomplete element from which to retrieve the primary value
        Returns: str: The primary value extracted from the element's attribute
        """
        return element.get_attribute("ac-value")
