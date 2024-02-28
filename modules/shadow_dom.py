from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from time import sleep


class AboutLogins:
    def __init__(self, driver: Firefox):
        self.driver = driver

    def add_login_button(self) -> WebElement:
        shadow_root = self.driver.find_element(
            By.CSS_SELECTOR, "login-list"
        ).shadow_root
        return shadow_root.find_element(By.CSS_SELECTOR, "create-login-button")

    def search_input(self) -> WebElement:
        shadow_root = self.driver.find_element(
            By.CSS_SELECTOR, "login-list"
        ).shadow_root
        return shadow_root.find_element(
            By.CSS_SELECTOR, "login-filter"
        ).shadow_root.find_element(By.CLASS_NAME, "filter")

    def login_item_by_type(self, login_type: str) -> WebElement:
        login_item_shadow_root = self.driver.find_element(
            By.CSS_SELECTOR, "login-item"
        ).shadow_root
        return login_item_shadow_root.find_element(By.NAME, login_type)

    def login_item_save_changes_button(self) -> WebElement:
        actions_row_shadow_root = self.driver.find_element(
            By.CLASS_NAME, "form-actions-row"
        ).shadow_root
        return login_item_shadow_root.find_element(By.CLASS_NAME, "save-changes-button")
