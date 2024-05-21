from selenium.webdriver.support import expected_conditions as EC

from modules.page_base import BasePage


class CreditCardPopup(BasePage):
    """Browser Object Model for Credit Card Popup"""

    URL_TEMPLATE = ""

    def verify_popup(self):
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.expect(
                EC.element_to_be_clickable(self.get_element("autofill-cc-panel"))
            )
