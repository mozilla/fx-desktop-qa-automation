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
        self.get_element("create-login-button").click()
        return self

    def create_new_login(self, form_info: dict) -> Page:
        ba = BrowserActions(self.driver)
        try:
            for item_type, value in form_info.items():
                ba.clear_and_fill(self.get_element("login-item-type", item_type), value)
            self.get_element("create-login-button")
        except (WebDriverException, StaleElementReferenceException):
            self.get_element("save-changes-button").click()
        return self
