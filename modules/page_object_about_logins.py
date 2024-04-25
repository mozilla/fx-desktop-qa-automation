from pypom import Page
from selenium.common.exceptions import (
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

    def __init__(self, driver):
        super().__init__(driver)
        self.load_element_manifest("./modules/data/about_logins.components.json")

    def click_add_login_button(self) -> Page:
        self.get_element("create-login-button").click()
        return self

    def create_new_login(self, form_info: dict) -> Page:
        ba = BrowserActions(self.driver)
        for item_type, value in form_info.items():
            ba.clear_and_fill(self.get_element("login-item-type", item_type), value)
        try:
            self.get_element("create-login-button")
        except WebDriverException:
            self.get_element("save-changes-button").click()
        return self
