from pypom import Page, Region
from modules.page_base import BasePage
from selenium.common.exceptions import (
    InvalidArgumentException,
    WebDriverException,
)
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

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

    @property
    def loaded(self):
        return EC.presence_of_element_located((By.CSS_SELECTOR, "login-list"))

    def add_login_button(self) -> WebElement:
        """Return the button that allows you to add a new login."""
        shadow_root = self.driver.find_element(
            By.CSS_SELECTOR, "login-list"
        ).shadow_root
        return shadow_root.find_element(By.CSS_SELECTOR, "create-login-button")

    def search_input(self) -> WebElement:
        """Return the login filter/search input"""
        shadow_root = self.driver.find_element(
            By.CSS_SELECTOR, "login-list"
        ).shadow_root
        return shadow_root.find_element(
            By.CSS_SELECTOR, "login-filter"
        ).shadow_root.find_element(By.CLASS_NAME, "filter")

    def login_item_by_type(self, login_type: str) -> WebElement:
        """Given a `login_type`, return the corresponding input from New Login view"""
        login_item_shadow_root = self.driver.find_element(
            By.CSS_SELECTOR, "login-item"
        ).shadow_root
        return login_item_shadow_root.find_element(By.NAME, login_type)

    def login_item_save_changes_button(self) -> WebElement:
        """Return the button that saves a new login."""
        actions_row_shadow_root = self.driver.find_element(
            By.CLASS_NAME, "form-actions-row"
        ).shadow_root
        return actions_row_shadow_root.find_element(
            By.CLASS_NAME, "save-changes-button"
        )

    def click_add_login_button(self) -> Page:
        self.add_login_button().click()
        return self

    def create_new_login(self, form_info: dict) -> Page:
        ba = BrowserActions(self.driver)
        for item_type, value in form_info.items():
            ba.clear_and_fill(self.login_item_by_type(item_type), value)
        try:
            self.add_login_button()
        except WebDriverException:
            self.login_item_save_changes_button().click()
        return self
