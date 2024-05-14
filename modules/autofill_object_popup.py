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
