from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class AboutLogins:
    """
    Page Object Model for about:logins, which goes through Shadow DOMs.

    Attributes
    ----------
    driver: selenium.webdriver.Firefox
        WebDriver object under test
    """

    def __init__(self, driver: Firefox):
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "login-list"))
        )
        self.driver = driver

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
