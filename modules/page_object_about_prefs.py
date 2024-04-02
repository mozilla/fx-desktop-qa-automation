from pypom import Page, Region
from selenium.common.exceptions import (
    InvalidArgumentException,
    WebDriverException,
)
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

from modules.util import BrowserActions, PomUtils


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
                el for el in self.shadow_elements if el.tag_name == "dropmarker"
            )

        @property
        def loaded(self):
            return self.root if EC.element_to_be_clickable(self.root) else False

        def select_option(self, option_name):
            if not self.dropmarker.get_attribute("open") == "true":
                self.root.click()
            matching_menuitems = [
                el
                for el in self.root.find_elements(By.CSS_SELECTOR, "menuitem")
                if el.get_attribute("label") == option_name
            ]
            if len(matching_menuitems) == 0:
                return False
            elif len(matching_menuitems) == 1:
                matching_menuitems[0].click()
                self.wait.until(EC.element_to_be_selected(matching_menuitems[0]))
                return matching_menuitems[0]
            else:
                raise ValueError("More than one menu item matched search string")

    def dropdown(self, selector: tuple[str, str]) -> Dropdown:
        menu_root = self.driver.find_element(*selector)
        return self.Dropdown(self, root=menu_root)

    def dropdown_with_current_value(self, value: str) -> Dropdown:
        menu_root = self.driver.find_element(
            By.CSS_SELECTOR, f"menulist[label='{value}']"
        )
        return self.Dropdown(self, root=menu_root)

    def dropdown_with_label(self, label: str) -> Dropdown:
        menu_root = self.driver.find_element(
            By.XPATH,
            f".//label[contains(., '{label}')]/following-sibling::hbox/menulist",
        )
        return self.Dropdown(self, root=menu_root)

    def search_engine_dropdown(self) -> Dropdown:
        return self.dropdown((By.ID, "defaultEngine"))
