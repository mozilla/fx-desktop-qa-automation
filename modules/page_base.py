import json
import re

from pypom import Page
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from modules.util import PomUtils

# Convert "strategy" from the components json to Selenium By vals
STRATEGY_MAP = {
    "css": By.CSS_SELECTOR,
    "class": By.CLASS_NAME,
    "id": By.ID,
    "link_text": By.LINK_TEXT,
    "partial_link_text": By.PARTIAL_LINK_TEXT,
    "xpath": By.XPATH,
    "tag": By.TAG_NAME,
    "name": By.NAME,
}


class BasePage(Page):
    def __init__(self, driver, **kwargs):
        super().__init__(driver, **kwargs)
        self.utils = PomUtils(self.driver)

        # JSON files should be labelled with snake_cased versions of the Class name
        qualname = self.__class__.__qualname__
        manifest_name = qualname[0].lower()
        for char in qualname[1:]:
            if char == char.lower():
                manifest_name += char
            else:
                manifest_name += f"_{char.lower()}"
        self.load_element_manifest(f"./modules/data/{manifest_name}.components.json")

    def expect(self, condition) -> Page:
        self.wait.until(condition)
        return self

    def load_element_manifest(self, manifest_loc):
        with open(manifest_loc) as fh:
            self.elements = json.load(fh)

    def get_selector(self, name: str, *label) -> list:
        """ """
        element_data = self.elements[name]
        selector = [
            STRATEGY_MAP[element_data["strategy"]],
            element_data["selectorData"],
        ]
        if not label:
            return selector
        braces = re.compile(r"(\{.*?\})")
        match = braces.findall(selector[1])
        for i in range(len(label)):
            selector[1] = selector[1].replace(match[i], label[i])
        return selector

    def get_element(self, name: str, *label):
        if "seleniumObject" in self.elements[name]:
            return self.elements[name]["seleniumObject"]
        element_data = self.elements[name]
        selector = self.get_selector(name, *label)
        if "shadowParent" in element_data:
            shadow_parent = self.get_element(element_data["shadowParent"])
            shadow_element = self.utils.find_shadow_element(shadow_parent, selector)
            self.elements[name]["seleniumObject"] = shadow_element
            return shadow_element
        found_element = self.driver.find_element(*selector)
        self.elements[name]["seleniumObject"] = found_element
        return found_element

    @property
    def loaded(self):
        return all(
            [
                EC.presence_of_element_located(
                    (STRATEGY_MAP[el["strategy"]], el["selectorData"])
                )
                for el in self.elements.values()
                if "requiredForPage" in el["groups"]
            ]
        )
