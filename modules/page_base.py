import json
import logging
import os
import platform
import re
from copy import deepcopy
from pathlib import Path
from typing import Union

from pypom import Page
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains, Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

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

    def __init__(self, driver: Firefox, **kwargs):
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
        sys_platform = self.sys_platform()
        if sys_platform == "Windows":
            root_dir = Path(os.getcwd())
            json_path = root_dir.joinpath("modules", "data")
            self.load_element_manifest(rf"{json_path}\{manifest_name}.components.json")
        else:
            self.load_element_manifest(
                f"./modules/data/{manifest_name}.components.json"
            )
        self.actions = ActionChains(self.driver)
        self.instawait = WebDriverWait(self.driver, 0)

    _xul_source_snippet = (
        'xmlns:xul="http://www.mozilla.org/keymaster/gatekeeper/there.is.only.xul"'
    )

    def sys_platform(self):
        return platform.system()

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
        if self.context == "chrome":
            with self.driver.context(self.driver.CONTEXT_CHROME):
                self.wait.until(condition)
        else:
            self.wait.until(condition)
        return self

    def expect_not(self, condition) -> Page:
        """Use the Page's to wait until assert a condition is not true or wait until timeout"""
        if self.context == "chrome":
            with self.driver.context(self.driver.CONTEXT_CHROME):
                self.wait.until_not(condition)
        else:
            self.wait.until_not(condition)
        return self

    def perform_key_combo(self, *keys) -> Page:
        """
        Use ActionChains to perform key combos. Modifier keys should come first in the function call.
        Usage example: perform_key_combo(Keys.CONTROL, Keys.ALT, "c") presses CTRL+ALT+c.
        """
        for k in keys[-1]:
            self.actions.key_down(k)
        self.actions.send_keys(keys[-1])
        self.actions.perform()
        return self

    def load_element_manifest(self, manifest_loc):
        """Populate self.elements with the parse of the elements JSON"""
        logging.info(f"Loading element manifest: {manifest_loc}")
        with open(manifest_loc) as fh:
            self.elements = json.load(fh)
        # We should expect an key-value pair of "context": "chrome" for Browser Objs
        if "context" in self.elements:
            self.context = self.elements["context"]
            del self.elements["context"]
        else:
            self.context = "content"

    def get_selector(self, name: str, labels=[]) -> list:
        """
        Given a key for a self.elements dict entry, return the Selenium selector tuple.
        If there are items in `labels`, replace instances of {.*} in the "selectorData"
        with items from `labels`, in the order they are given. (Think Rust format macros.)

        ...

        Arguments
        ---------

        name: str
            The key of the entry in self.elements, parsed from the elements JSON

        labels: list[str]
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
        if not labels:
            return selector
        braces = re.compile(r"(\{.*?\})")
        match = braces.findall(selector[1])
        for i in range(len(labels)):
            logging.info(f"Replace {match[i]} with {labels[i]}")
            selector[1] = selector[1].replace(match[i], labels[i])
        return selector

    def get_element(
        self, name: str, multiple=False, labels=[]
    ) -> Union[list[WebElement], WebElement]:
        """
        Given a key for a self.elements dict entry, return the Selenium WebElement(s).
        If multiple is set to True, use find_elements instead of find_element.
        If there are items in `labels`, replace instances of {.*} in the "selectorData"
        with items from `labels`, in the order they are given. (Think Rust format macros.)

        ...

        Arguments
        ---------

        name: str
            The key of the entry in self.elements, parsed from the elements JSON

        multiple: bool
            Do we expect a list of WebElements?

        labels: list[str]
            Strings that replace instances of {.*} in the "selectorData" subentry of
            self.elements[name]

        Returns
        -------

        selenium.webdriver.remote.webelement.WebElement
            The WebElement object referred to by the element dict.
        """
        logging.info("====")
        if not multiple:
            logging.info(f"Getting element {name}")
        else:
            logging.info(f"Getting multiple elements by name {name}")
        if labels:
            logging.info(f"Labels: {labels}")
        cache_name = name
        if labels:
            labelscode = "".join(labels)
            cache_name = f"{name}{labelscode}"
            if cache_name not in self.elements:
                self.elements[cache_name] = deepcopy(self.elements[name])

        if not multiple and "seleniumObject" in self.elements[cache_name]:
            # no caching for multiples
            cached_element = self.elements[cache_name]["seleniumObject"]
            try:
                self.instawait.until_not(EC.staleness_of(cached_element))
                logging.info(f"Returned {cache_name} from object cache!")
                return self.elements[cache_name]["seleniumObject"]
            except (TimeoutError, TimeoutException):
                # Because we have a timeout of 0, this should not cause delays
                pass
        element_data = self.elements[cache_name]
        selector = self.get_selector(cache_name, labels)
        if "shadowParent" in element_data:
            logging.info(f"Found shadow parent {element_data['shadowParent']}...")
            shadow_parent = self.get_element(element_data["shadowParent"])
            if not multiple:
                shadow_element = self.utils.find_shadow_element(
                    shadow_parent, selector, context=self.context
                )
                if "doNotCache" not in element_data["groups"]:
                    self.elements[cache_name]["seleniumObject"] = shadow_element
                return shadow_element
            else:
                # no caching for multiples
                return self.utils.find_shadow_element(
                    shadow_parent, selector, multiple=multiple, context=self.context
                )
        if not multiple:
            found_element = self.driver.find_element(*selector)
            if "doNotCache" not in element_data["groups"]:
                self.elements[cache_name]["seleniumObject"] = found_element
            logging.info(f"Returning element {cache_name}.\n")
            return found_element
        else:
            return self.driver.find_elements(*selector)

    def get_elements(self, name: str, labels=[]):
        return self.get_element(name, multiple=True, labels=labels)

    def element_exists(self, name: str, *labels) -> Page:
        self.expect(
            EC.presence_of_element_located(self.get_selector(name, labels=labels))
        )
        return self

    def element_visible(self, name: str, *labels) -> Page:
        self.expect(EC.visibility_of(self.get_element(name, labels=labels)))
        return self

    def element_clickable(self, name: str, *labels) -> Page:
        self.expect(EC.element_to_be_clickable(self.get_element(name, labels=labels)))
        return self

    def element_selected(self, name: str, *labels) -> Page:
        self.expect(EC.element_to_be_selected(self.get_element(name, labels=labels)))
        return self

    def double_click(self, name: str, label: str):
        elem = self.get_element(name, labels=[label])
        EC.element_to_be_clickable(elem)
        self.actions.double_click(elem).perform()

    @property
    def loaded(self):
        """
        Here, we're using our own get_elements to ensure that all elements that
        are requiredForPage are gettable before we return loaded as True
        """
        _loaded = False
        try:
            if self.context == "chrome":
                self.set_chrome_context()
            for name in self.elements:
                if "requiredForPage" in self.elements[name]["groups"]:
                    logging.info(f"ensuring {name} in DOM...")
                    self.get_element(name)
            _loaded = True
        except (TimeoutError, TimeoutException):
            pass
        self.set_content_context()
        return _loaded
