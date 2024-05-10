from pypom import Region
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from modules.page_base import BasePage
from modules.util import PomUtils


class AboutPrefs(BasePage):
    """Page Object Model for about:preferences"""

    URL_TEMPLATE = "about:preferences#{category}"

    class Dropdown(Region):
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
                return self
            else:
                raise ValueError("More than one menu item matched search string")

    def search_engine_dropdown(self) -> Dropdown:
        return self.Dropdown(self, root=self.get_element("search-engine-dropdown-root"))

    def find_in_settings(self, term: str) -> BasePage:
        search_input = self.get_element("find-in-settings-input")
        search_input.clear()
        search_input.send_keys(term)
        return self

    def find_setting_and_click(self, field_name: str):
        # with self.driver.context(self.driver.CONTEXT_CHROME):
        self.get_element(field_name).click()
