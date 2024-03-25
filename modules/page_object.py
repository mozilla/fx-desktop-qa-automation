from pypom import Page, Region
from selenium.common.exceptions import (
    InvalidArgumentException,
    WebDriverException,
)
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

from modules.util import BrowserActions


class PomUtils:
    def __init__(self, driver: Firefox):
        self.driver = driver

    def get_shadow_content(self, element: WebElement) -> list[WebElement]:
        try:
            shadow_root = element.shadow_root
            return [shadow_root]
        except InvalidArgumentException:
            shadow_children = self.driver.execute_script(
                "return arguments[0].shadowRoot.children", element
            )
            if len(shadow_children) and shadow_children[0] is not None:
                return shadow_children


class AboutPrefs(Page):
    """Page Object Model for about:preferences"""

    URL_TEMPLATE = "about:preferences#{category}"

    def __init__(self, driver, **kwargs):
        super().__init__(driver, timeout=10, **kwargs)
        self.utils = PomUtils(self.driver)

    class Dropdown(Region):
        _active_dropdown_item = (By.CSS_SELECTOR, "menuitem[_moz-menuactive='true']")

        def __init__(self, page, **kwargs):
            super().__init__(page, **kwargs)
            self.utils = PomUtils(self.driver)
            self.shadow_elements = self.utils.get_shadow_content(self.root)
            self.dropmarker = next(
                e for e in self.shadow_elements if e.tag_name == "dropmarker"
            )

        @property
        def loaded(self):
            return self.root if EC.element_to_be_clickable(self.root) else False

        def select_option(self, option_name):
            if not self.dropmarker.get_attribute("open") == "true":
                self.root.click()
            matching_menuitems = [
                e
                for e in self.root.find_elements(By.CSS_SELECTOR, "menuitem")
                if e.get_attribute("label") == option_name
            ]
            if len(matching_menuitems) == 0:
                return False
            elif len(matching_menuitems) == 1:
                matching_menuitems[0].click()
                self.wait.until(EC.element_to_be_selected(matching_menuitems[0]))
                return matching_menuitems[0]
            else:
                raise ValueError("More than one menu item matched search string")

    def get_dropdown(self, selector: tuple[str, str]) -> Dropdown:
        menu_root = self.driver.find_element(*selector)
        return self.Dropdown(self, root=menu_root)

    def get_dropdown_by_current_value(self, value: str) -> Dropdown:
        menu_root = self.driver.find_element(
            By.CSS_SELECTOR, f"menulist[label='{value}']"
        )
        return self.Dropdown(self, root=menu_root)

    def get_dropdown_by_label(self, label: str) -> Dropdown:
        menu_root = self.driver.find_element(
            By.XPATH,
            f".//label[contains(., '{label}')]/following-sibling::hbox/menulist",
        )
        return self.Dropdown(self, root=menu_root)

    def get_search_engine_dropdown(self) -> Dropdown:
        return self.get_dropdown((By.ID, "defaultEngine"))


class AboutGlean(Page):
    """Page Object Model for about:glean"""

    URL_TEMPLATE = "about:glean"

    # Elements
    _ping_id_input = (By.ID, "tag-pings")
    _submit_button = (By.ID, "controls-submit")

    def change_ping_id(self, ping_id: str):
        ba = BrowserActions(self.driver)
        ping_input = self.driver.find_element(*self._ping_id_input)
        ba.clear_and_fill(ping_input, ping_id)
        self.wait.until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR, f"label[for='{self._submit_button[1]}']"), ping_id
            )
        )
        self.driver.find_element(*self._submit_button).click()


class AboutLogins(Page):
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

    def create_new_login(self, form_info: dict):
        ba = BrowserActions(self.driver)
        for item_type, value in form_info.items():
            ba.clear_and_fill(self.login_item_by_type(item_type), value)
        try:
            self.add_login_button()
        except WebDriverException:
            self.login_item_save_changes_button().click()
