import json
import logging
import re

from pypom import Page
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
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
    """
    This class extends pypom.Page with a constructor and methods to support our testing.

    Page objects will now expect a JSON entry in ./modules/data with info about elements'
    selectors, locations in shadow DOM, and other categorizations. This JSON file should
    be name filename.components.json, where filename is the snake_case version of the
    class name. E.g. AboutPrefs has ./modules/data/about_prefs.components.json.

    Elements in the "requiredForPage" group will be checked for presence before self.loaded
    can return True.

    ...

    Attributes
    ----------
    driver: selenium.webdriver.Firefox
        The browser instance under test

    utils: modules.utils.PomUtils
        POM utilities for the object

    elements: dict
        Parse of the elements JSON file
    """

    def __init__(self, driver, **kwargs):
        super().__init__(driver, **kwargs)
        self.utils = PomUtils(self.driver)

        # JSON files should be labelled with snake_cased versions of the Class name
        qualname = self.__class__.__qualname__
        logging.info("======")
        logging.info(f"Loading POM for {qualname}...")
        manifest_name = qualname[0].lower()
        for char in qualname[1:]:
            if char == char.lower():
                manifest_name += char
            else:
                manifest_name += f"_{char.lower()}"
        self.load_element_manifest(f"/Users/virgil.sangerean/Documents/GitHub/fx-desktop-qa-automation/modules/data/{manifest_name}.components.json")

    _xul_source_snippet = (
        'xmlns:xul="http://www.mozilla.org/keymaster/gatekeeper/there.is.only.xul"'
    )

    def set_chrome_context(self):
        """Make sure the Selenium driver is using CONTEXT_CHROME"""
        if self._xul_source_snippet not in self.driver.page_source:
            self.driver.set_context(self.driver.CONTEXT_CHROME)

    def set_content_context(self):
        """Make sure the Selenium driver is using CONTEXT_CONTENT"""
        if self._xul_source_snippet in self.driver.page_source:
            self.driver.set_context(self.driver.CONTEXT_CONTENT)

    def expect(self, condition) -> Page:
        """Use the Page's wait object to assert a condition or wait until timeout"""
        self.wait.until(condition)
        return self

    def load_element_manifest(self, manifest_loc):
        """Populate self.elements with the parse of the elements JSON"""
        logging.info(f"Loading element manifest: {manifest_loc}")
        with open(manifest_loc) as fh:
            self.elements = json.load(fh)

    def get_selector(self, name: str, *label) -> list:
        """
        Given a key for a self.elements dict entry, return the Selenium selector tuple.
        If there are items in `label`, replace instances of {.*} in the "selectorData"
        with items from `label`, in the order they are given. (Think Rust format macros.)

        ...

        Arguments
        ---------

        name: str
            The key of the entry in self.elements, parsed from the elements JSON

        *label: *str
            Strings that replace instances of {.*} in the "selectorData" subentry of
            self.elements[name]

        Returns
        -------
        list
            The Selenium selector tuple (as a list)
        """
        logging.info(f"Get selector for {name}...")
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
            logging.info(f"Replace {match[i]} with {label[i]}")
            selector[1] = selector[1].replace(match[i], label[i])
        return selector

    def get_element(self, name: str, *label) -> WebElement:
        """
        Given a key for a self.elements dict entry, return the Selenium WebElement.
        If there are items in `label`, replace instances of {.*} in the "selectorData"
        with items from `label`, in the order they are given. (Think Rust format macros.)

        ...

        Arguments
        ---------

        name: str
            The key of the entry in self.elements, parsed from the elements JSON

        *label: *str
            Strings that replace instances of {.*} in the "selectorData" subentry of
            self.elements[name]

        Returns
        -------

        selenium.webdriver.remote.webelement.WebElement
            The WebElement object referred to by the element dict.
        """
        logging.info("====")
        logging.info(f"Getting element {name}")
        if "seleniumObject" in self.elements[name]:
            logging.info("Returned from object cache!")
            return self.elements[name]["seleniumObject"]
        element_data = self.elements[name]
        selector = self.get_selector(name, *label)
        if "shadowParent" in element_data:
            logging.info(f"Found shadow parent {element_data['shadowParent']}...")
            shadow_parent = self.get_element(element_data["shadowParent"])
            shadow_element = self.utils.find_shadow_element(shadow_parent, selector)
            self.elements[name]["seleniumObject"] = shadow_element
            return shadow_element
        found_element = self.driver.find_element(*selector)
        self.elements[name]["seleniumObject"] = found_element
        logging.info(f"Returning element {name}.\n")
        return found_element

    def element_exists(self, name: str, *label) -> Page:
        self.expect(EC.presence_of_element_located(self.get_selector(name, *label)))
        return self

    def element_visible(self, name: str, *label) -> Page:
        self.expect(EC.visibility_of(self.get_element(name, *label)))
        return self

    def element_clickable(self, name: str, *label) -> Page:
        self.expect(EC.element_to_be_clickable(self.get_element(name, *label)))
        return self

    def element_selected(self, name: str, *label) -> Page:
        self.expect(EC.element_to_be_selected(self.get_element(name, *label)))
        return self

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
