import logging

from pypom import Page
from selenium.common.exceptions import (
    StaleElementReferenceException,
    WebDriverException,
)

from modules.page_base import BasePage
from modules.util import BrowserActions


class AboutLogins(BasePage):
    """
    Page Object Model for about:logins, which goes through Shadow DOMs.

    Attributes
    ----------
    driver: selenium.webdriver.Firefox
        WebDriver object under test
    """

    URL_TEMPLATE = "about:logins"

    def click_add_login_button(self) -> Page:
        """Click the Add Login button"""
        self.get_element("create-login-button").click()
        logging.info("Clicked add login button")
        return self

    def create_new_login(self, form_info: dict) -> Page:
        """
        Given a dict with keys that match the valid item types in the
        new login dialog, create a new login with those values through UI.
        """
        ba = BrowserActions(self.driver)
        try:
            for item_type, value in form_info.items():
                logging.info(f"Filling {item_type} with {value}")
                ba.clear_and_fill(
                    self.get_element("login-item-type", labels=[item_type]), value
                )
            logging.info("Clicking submit...")
            self.get_element("create-login-button")
            logging.info("Submitted.")
        except (WebDriverException, StaleElementReferenceException):
            logging.info("Element not found or stale, pressing 'Save Changes'")
            self.get_element("save-changes-button").click()
            logging.info("Pressed.")
        return self
