import json

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

from modules.page_base import BasePage


class AutofillPopup(BasePage):
    """
    Page Object Model for the popups that have to do with autofill
    """

    URL_TEMPLATE = ""

    def press_doorhanger_save(self):
        """
        Presses the save button on the doorhanger popup.
        """
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.get_element("doorhanger-save-button").click()

    def verify_no_popup_panel(self):
        """
        Verifies that the autofill popup does NOT appear.
        """
        with self.driver.context(self.driver.CONTEXT_CHROME):
            element = self.get_element("autofill-panel")
            self.expect_not(EC.element_to_be_clickable(element))

    def hover_over_element(self, element: str):
        """
        Hover over the specified element.
        Parameters: element (str): The element to hover over.
        """
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.actions.move_to_element(element).perform()
            return self

    def get_nth_element(self, index: str) -> WebElement:
        """
        Get the nth element from the autocomplete list.
        Parameters: index (str): The index of the element to retrieve (1-based).
        Returns: WebElement: The nth element in the autocomplete list.
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

    # This is now just a bare value, not JSON (as of 128.0b3), please update your Firefox under test
    def get_primary_value(self, element):
        """
        Get the primary value from the autocomplete element.
        Parameters: element (WebElement): The autocomplete element from which to retrieve the primary value.
        Returns: str: The primary value extracted from the element's attribute.
        """
        with self.driver.context(self.driver.CONTEXT_CHROME):
            ac_value = element.get_attribute("ac-value")
            return ac_value

    def press_doorhanger_dropdown(self):
        """
        Presses the button beside Not now which toggles the dropdown menu in the doorhanger
        """
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.get_element("doorhanger-dropdown-button").click()

    def press_doorhanger_dropdown_never_save_cards(self):
        """
        Assuming that you have clicked Not Now in the doorhanger, this will click the Never Save Cards option
        """
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.get_element("doorhanger-dropdown-button-never-save-cards").click()

    def press_doorhanger_update(self):
        """
        Presses the update button on the doorhanger popup.
        """
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.get_element("doorhanger-update-button").click()
        return self
