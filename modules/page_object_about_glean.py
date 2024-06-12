from pypom import Page
from selenium.webdriver.support import expected_conditions as EC

from modules.page_base import BasePage
from modules.util import BrowserActions


class AboutGlean(BasePage):
    """
    Page Object Model for about:glean

    Attributes
    ----------
    driver: selenium.webdriver.Firefox
        WebDriver object under test
    """

    URL_TEMPLATE = "about:glean"

    def change_ping_id(self, ping_id: str) -> Page:
        """
        Change the Glean ping id to the given string.
        """
        ba = BrowserActions(self.driver)
        ping_input = self.get_element("ping-id-input")
        ba.clear_and_fill(ping_input, ping_id)
        self.wait.until(
            EC.text_to_be_present_in_element(
                self.get_selector("ping-submit-label"), ping_id
            )
        )
        self.get_element("ping-submit-button").click()
        return self
