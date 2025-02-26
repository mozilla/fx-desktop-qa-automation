import json
import logging
import os
import platform
import re
import time
from copy import deepcopy
from functools import wraps
from pathlib import Path
from typing import List, Union

from pynput.keyboard import Controller, Key
from pypom import Page
from selenium.common import NoAlertPresentException
from selenium.common.exceptions import (
    NoSuchElementException,
    NoSuchWindowException,
    TimeoutException,
)
from selenium.webdriver import ActionChains, Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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
        """Return the system platform name"""
        return platform.system()

    def set_chrome_context(self):
        """Make sure the Selenium driver is using CONTEXT_CHROME"""
        if self._xul_source_snippet not in self.driver.page_source:
            self.driver.set_context(self.driver.CONTEXT_CHROME)

    @staticmethod
    def context_chrome(func):
        """Decorator to switch to CONTEXT_CHROME"""

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            with self.driver.context(self.driver.CONTEXT_CHROME):
                return func(self, *args, **kwargs)

        return wrapper

    @staticmethod
    def context_content(func):
        """Decorator to switch to CONTEXT_CONTENT"""

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            with self.driver.context(self.driver.CONTEXT_CONTENT):
                return func(self, *args, **kwargs)

        return wrapper

    def set_content_context(self):
        """Make sure the Selenium driver is using CONTEXT_CONTENT"""
        if self._xul_source_snippet in self.driver.page_source:
            self.driver.set_context(self.driver.CONTEXT_CONTENT)

    def opposite_context(self):
        """Return the context that is *not* in use"""
        return (
            self.driver.CONTEXT_CONTENT
            if self._xul_source_snippet in self.driver.page_source
            else self.driver.CONTEXT_CHROME
        )

    def is_private(self):
        """Determine if current browsing context is private"""
        with self.driver.context(self.driver.CONTEXT_CHROME):
            return "Private Browsing" in self.driver.title

    def custom_wait(self, **kwargs) -> WebDriverWait:
        """
        Create a custom WebDriverWait object, refer to Selenium docs
        for explanations of the arguments.
        Examples:
          self.custom_wait(timeout=45).until(<condition>)
          self.custom_wait(poll_frequency=1).until(<condition>)
        """
        return WebDriverWait(self.driver, **kwargs)

    def expect(self, condition) -> Page:
        """Use the Page's wait object to assert a condition or wait until timeout"""
        with self.driver.context(self.context_id):
            logging.info(f"Expecting in {self.context_id}...")
            self.wait.until(condition)
        return self

    def expect_not(self, condition) -> Page:
        """Use the Page's to wait until assert a condition is not true or wait until timeout"""
        with self.driver.context(self.context_id):
            logging.info(f"Expecting NOT in {self.context_id}...")
            self.wait.until_not(condition)
        return self

    def perform_key_combo(self, *keys) -> Page:
        """
        Use ActionChains to perform key combos. Modifier keys should come first in the function call.
        Usage example: perform_key_combo(Keys.CONTROL, Keys.ALT, "c") presses CTRL+ALT+c.
        """
        while Keys.CONTROL in keys and self.sys_platform == "Darwin":
            keys[keys.index(Keys.CONTROL)] = Keys.COMMAND
        for k in keys[:-1]:
            self.actions.key_down(k)

        self.actions.send_keys(keys[-1])

        for k in keys[:-1]:
            self.actions.key_up(k)

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
            self.context_id = (
                self.driver.CONTEXT_CHROME
                if self.context == "chrome"
                else self.driver.CONTEXT_CONTENT
            )
            del self.elements["context"]
        else:
            self.context = "content"
            self.context_id = self.driver.CONTEXT_CONTENT
        # If we find a key-value pair for "do-not-cache", add all elements to that group
        doNotCache = self.elements.get("do-not-cache")
        if "do-not-cache" in self.elements:
            del self.elements["do-not-cache"]
        if doNotCache:
            for key in self.elements.keys():
                logging.info(f"adding do-not-cache to {key}")
                self.elements[key]["groups"].append("doNotCache")

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
            logging.info("Returned selector.")
            return selector
        braces = re.compile(r"(\{.*?\})")
        match = braces.findall(selector[1])
        for i in range(len(labels)):
            logging.info(f"Replace {match[i]} with {labels[i]}")
            selector[1] = selector[1].replace(match[i], labels[i], 1)
        logging.info("Returned selector.")
        return selector

    def get_element(
        self, name: str, multiple=False, parent_element=None, labels=[]
    ) -> Union[list[WebElement], WebElement]:
        """
        Given a key for a self.elements dict entry, return the Selenium WebElement(s).
        If multiple is set to True, use find_elements instead of find_element.
        If there are items in `labels`, replace instances of {.*} in the "selectorData"
        with items from `labels`, in the order they are given. (Think Rust format macros.)


        Note: This method currently does not support finding a child under a parent (given in the JSON) if it has a shadow parent.
        ...

        Arguments
        ---------

        name: str
            The key of the entry in self.elements, parsed from the elements JSON

        multiple: bool
            Do we expect a list of WebElements?

        parent_element: WebElement
            The parent WebElement to search under to narrow the scope instead of searching the entire page

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
        logging.info(f"Groups: {self.elements[name]['groups']}")
        cache_name = name
        if labels:
            labelscode = "".join(labels)
            cache_name = f"{name}{labelscode}"
            if cache_name not in self.elements:
                self.elements[cache_name] = deepcopy(self.elements[name])
        if multiple:
            logging.info(f"Multiples: Not caching {cache_name}...")
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
                    logging.info(f"Not caching {cache_name}...")
                    self.elements[cache_name]["seleniumObject"] = shadow_element
                return shadow_element
            else:
                # no caching for multiples
                return self.utils.find_shadow_element(
                    shadow_parent, selector, multiple=multiple, context=self.context
                )
        # if the child has a parent tag
        if parent_element is not None:
            logging.info("A WebElement parent was detected.")
            if not multiple:
                child_element = parent_element.find_element(*selector)
                if "doNotCache" not in element_data["groups"]:
                    self.elements[cache_name]["seleniumObject"] = child_element
                logging.info(f"Returning element {cache_name}.\n")
                return child_element
            else:
                return parent_element.find_elements(*selector)
        if not multiple:
            found_element = self.driver.find_element(*selector)
            if "doNotCache" not in element_data["groups"]:
                logging.info(f"Caching {cache_name}...")
                self.elements[cache_name]["seleniumObject"] = found_element
            logging.info(f"Returning element {cache_name}.\n")
            return found_element
        else:
            return self.driver.find_elements(*selector)

    def get_elements(self, name: str, labels=[]):
        """
        Get multiple elements using get_element()

        Arguments
        ---------

        name: str
            The key of the entry in self.elements, parsed from the elements JSON

        labels: list[str]
            Strings that replace instances of {.*} in the "selectorData" subentry of
            self.elements[name]

        Returns
        -------

        list[selenium.webdriver.remote.webelement.WebElement]
            The WebElement objects referred to by the element dict.
        """
        return self.get_element(name, multiple=True, labels=labels)

    def get_parent_of(
        self, reference: Union[str, tuple, WebElement], labels=[]
    ) -> WebElement:
        """
        Given a name + labels, a WebElement, or a tuple, return the direct parent node of the element.
        """

        child = self.fetch(reference, labels=labels)
        return child.find_element(By.XPATH, "..")

    def element_exists(self, name: str, labels=[]) -> Page:
        """Expect helper: wait until element exists or timeout"""
        self.expect(lambda _: self.get_element(name, labels=labels))
        return self

    def element_does_not_exist(self, name: str, labels=[]) -> Page:
        """Expect helper: wait until element exists or timeout"""
        self.instawait.until_not(lambda _: self.get_elements(name, labels=labels))
        return self

    def element_visible(self, name: str, labels=[]) -> Page:
        """Expect helper: wait until element is visible or timeout"""
        self.expect(
            lambda _: self.get_element(name, labels=labels)
            and self.get_element(name, labels=labels).is_displayed()
        )
        return self

    def element_not_visible(self, name: str, labels=[]) -> Page:
        """Expect helper: wait until element is not visible or timeout"""
        self.expect(
            lambda _: self.get_elements(name, labels=labels) == []
            or not self.get_element(name, labels=labels).is_displayed()
        )
        return self

    def element_clickable(self, name: str, labels=[]) -> Page:
        """Expect helper: wait until element is clickable or timeout"""
        self.element_visible(name, labels=labels)
        self.expect(lambda _: self.get_element(name, labels=labels).is_enabled())
        return self

    def element_selected(self, name: str, labels=[]) -> Page:
        """Expect helper: wait until element is selected or timeout"""
        self.expect(
            lambda _: self.get_element(name, labels=labels)
            and self.get_element(name, labels=labels).is_selected()
        )
        return self

    def element_has_text(self, name: str, text: str, labels=[]) -> Page:
        """Expect helper: wait until element has given text"""
        self.expect(lambda _: text in self.get_element(name, labels=labels).text)
        return self

    def element_attribute_contains(
        self, name: str, attr_name: str, attr_value: Union[str, float, int], labels=[]
    ) -> Page:
        """Expect helper: wait until element attribute contains certain value"""
        self.expect(
            lambda _: self.get_element(name, labels=labels)
            and str(attr_value)
            in self.get_element(name, labels=labels).get_attribute(attr_name)
        )
        return self

    def url_contains(self, url_part: str) -> Page:
        """Expect helper: wait until driver URL contains given text or timeout"""
        self.context_id = self.driver.CONTEXT_CONTENT
        self.expect(EC.url_contains(url_part))
        return self

    def title_contains(self, url_part: str) -> Page:
        """Expect helper: wait until driver URL contains given text or timeout"""
        self.expect(EC.title_contains(url_part))
        return self

    def verify_opened_image_url(self, url_substr: str, pattern: str) -> Page:
        """
        Given a part of a URL and a regex, wait for that substring to exist in
        the current URL, then match the regex against the current URL.
        (This gives us the benefit of fast failure.)
        """
        self.url_contains(url_substr)
        current_url = self.driver.current_url

        assert re.match(pattern, current_url), (
            f"URL does not match the expected pattern: {current_url}"
        )
        return self

    def fill(
        self, name: str, term: str, clear_first=True, press_enter=True, labels=[]
    ) -> Page:
        """
        Get a fillable element and fill it with text. Return self.

        ...

        Arguments
        ---------

        name: str
            The key of the entry in self.elements, parsed from the elements JSON

        labels: list[str]
            Strings that replace instances of {.*} in the "selectorData" subentry of
            self.elements[name]

        term: str
            The text to enter into the element

        clear_first: bool
            Call .clear() on the element first. Default True

        press_enter: bool
            Press Keys.ENTER after filling the element. Default True
        """
        if self.context == "chrome":
            self.set_chrome_context()
        el = self.get_element(name, labels=labels)
        self.element_clickable(name, labels=labels)
        if clear_first:
            el.clear()
        end = Keys.ENTER if press_enter else ""
        el.send_keys(f"{term}{end}")
        return self

    def fetch(self, reference: Union[str, tuple, WebElement], labels=[]) -> WebElement:
        """
        Given an element name, a selector, or a WebElement, return the
        corresponding WebElement.
        """
        if isinstance(reference, str):
            return self.get_element(reference, labels=labels)
        elif isinstance(reference, tuple):
            return self.find_element(*reference)
        elif isinstance(reference, WebElement):
            return reference
        assert False, (
            "Bad fetch: only selectors, selector names, or WebElements allowed."
        )

    def click_on(self, reference: Union[str, tuple, WebElement], labels=[]) -> Page:
        """Click on an element, no matter the context, return the page"""
        with self.driver.context(self.context_id):
            self.fetch(reference, labels).click()
            logging.info(f"{reference} clicked")
        return self

    def multi_click(
        self, iters: int, reference: Union[str, tuple, WebElement], labels=[]
    ) -> Page:
        """Perform multiple clicks at once on an element by name, selector, or WebElement"""
        with self.driver.context(self.context_id):
            el = self.fetch(reference, labels)

            def execute_multi_click():
                if iters == 2:
                    self.actions.double_click(el).perform()
                else:
                    for _ in range(iters):
                        self.actions.click(el)
                    self.actions.perform()

            # Little cheat: if element doesn't exist in one context, try the other
            try:
                execute_multi_click()
            except NoSuchElementException:
                with self.driver.context(self.opposite_context()):
                    execute_multi_click()

        return self

    def double_click(self, reference: Union[str, tuple, WebElement], labels=[]) -> Page:
        """Actions helper: perform double-click on given element"""
        return self.multi_click(2, reference, labels)

    def triple_click(self, reference: Union[str, tuple, WebElement], labels=[]) -> Page:
        """Actions helper: perform triple-click on a given element"""
        return self.multi_click(3, reference, labels)

    def context_click(
        self, reference: Union[str, tuple, WebElement], labels=[]
    ) -> Page:
        """Context (right-) click on an element"""
        with self.driver.context(self.context_id):
            el = self.fetch(reference, labels)
            self.actions.context_click(el).perform()
        return self

    def copy(self) -> Page:
        """Copy the selected item"""
        mod_key = Keys.COMMAND if self.sys_platform() == "Darwin" else Keys.CONTROL
        self.actions.key_down(mod_key)
        self.actions.send_keys("c")
        self.actions.key_up(mod_key).perform()
        time.sleep(0.5)
        return self

    def paste(self) -> Page:
        """Paste the copied item"""
        mod_key = Keys.COMMAND if self.sys_platform() == "Darwin" else Keys.CONTROL
        self.actions.key_down(mod_key)
        self.actions.send_keys("v")
        self.actions.key_up(mod_key).perform()
        time.sleep(0.5)
        return self

    def undo(self) -> Page:
        """Undo last action"""
        mod_key = Keys.COMMAND if self.sys_platform() == "Darwin" else Keys.CONTROL
        self.actions.key_down(mod_key)
        self.actions.send_keys("z")
        self.actions.key_up(mod_key).perform()
        time.sleep(0.5)
        return self

    def paste_to_element(
        self, sys_platform, reference: Union[str, tuple, WebElement], labels=[]
    ) -> Page:
        """Paste the copied item into the element"""
        with self.driver.context(self.context_id):
            el = self.fetch(reference, labels)
            self.scroll_to_element(el)
            mod_key = Keys.COMMAND if sys_platform == "Darwin" else Keys.CONTROL
            self.actions.key_down(mod_key)
            self.actions.send_keys_to_element(el, "v")
            self.actions.key_up(mod_key).perform()
        return self

    def copy_image_from_element(
        self, keyboard, reference: Union[str, tuple, WebElement], labels=[]
    ) -> Page:
        """Copy from the given element using right click (pynput)"""
        with self.driver.context(self.context_id):
            el = self.fetch(reference, labels)
            self.scroll_to_element(el)
            self.context_click(el)
            keyboard.tap(Key.down)
            keyboard.tap(Key.down)
            keyboard.tap(Key.down)
            keyboard.tap(Key.enter)
            time.sleep(0.5)
        return self

    def copy_selection(
        self, keyboard, reference: Union[str, tuple, WebElement], labels=[]
    ) -> Page:
        """Copy from the current selection using right click (pynput)"""
        with self.driver.context(self.context_id):
            el = self.fetch(reference, labels)
            self.scroll_to_element(el)
            self.context_click(el)
            keyboard.tap(Key.down)
            keyboard.tap(Key.enter)
            time.sleep(0.5)
        return self

    def click_and_hide_menu(
        self, reference: Union[str, tuple, WebElement], labels=[]
    ) -> Page:
        """Click an option in a context menu, then hide it"""
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.fetch(reference, labels=labels).click()
            self.hide_popup_by_child_node(reference, labels=labels)
            return self

    def hover(self, reference: Union[str, tuple, WebElement], labels=[]):
        """
        Hover over the specified element.
        Parameters: element (str): The element to hover over.

        Default tries to hover something in the chrome context
        """
        with self.driver.context(self.context_id):
            el = self.fetch(reference, labels)
            self.actions.move_to_element(el).perform()
        return self

    def scroll_to_element(self, reference: Union[str, tuple, WebElement], labels=[]):
        """
        Scroll towards the specified element which may be out of frame.
        Parameters: element (str): The element to hover over.
        """
        with self.driver.context(self.context_id):
            el = self.fetch(reference, labels)
            self.driver.execute_script("arguments[0].scrollIntoView();", el)
        return self

    def get_all_children(
        self, reference: Union[str, tuple, WebElement], labels=[]
    ) -> List[WebElement]:
        """
        Gets all the children of a webelement
        """
        children = None
        with self.driver.context(self.context_id):
            element = self.fetch(reference, labels)
            children = element.find_elements(By.XPATH, "./*")
        return children

    def wait_for_no_children(
        self, parent: Union[str, tuple, WebElement], labels=[]
    ) -> Page:
        """
        Waits for 0 children under the given parent, the wait is instant (note, this changes the driver implicit wait and changes it back)
        """
        driver_wait = self.driver.timeouts.implicit_wait
        self.driver.implicitly_wait(0)
        try:
            assert len(self.get_all_children(self.fetch(parent, labels))) == 0
        finally:
            self.driver.implicitly_wait(driver_wait)

    def wait_for_num_tabs(self, num_tabs: int) -> Page:
        """
        Waits for the driver.window_handles to be updated accordingly with the number of tabs requested
        """
        try:
            self.wait.until(lambda _: len(self.driver.window_handles) == num_tabs)
        except TimeoutException:
            logging.warn("Timeout waiting for the number of windows to be:", num_tabs)
        return self

    def switch_to_new_tab(self) -> Page:
        """Get list of all window handles, switch to the newly opened tab"""
        self.driver.switch_to.window(self.driver.window_handles[-1])
        return self

    def wait_for_num_windows(self, num: int) -> Page:
        """Wait for the number of open tabs + windows to equal given int"""
        with self.driver.context(self.driver.CONTEXT_CONTENT):
            return self.wait_for_num_tabs(num)

    def switch_to_new_window(self) -> Page:
        """Switch to newest window"""
        with self.driver.context(self.driver.CONTEXT_CONTENT):
            return self.switch_to_new_tab()

    def switch_to_new_private_window(self) -> Page:
        "Switch to new private window"
        non_private_window = self.driver.current_window_handle
        original_window_idx = self.driver.window_handles.index(non_private_window)
        private_window = self.driver.window_handles[1 - original_window_idx]
        self.driver.switch_to.window(private_window)
        return self

    def switch_to_frame(self, frame: str, labels=[]) -> Page:
        """Switch to inline document frame"""
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.expect(
                EC.frame_to_be_available_and_switch_to_it(
                    self.get_selector(frame, labels=labels)
                )
            )
        return self

    def hide_popup(self, context_menu: str, chrome=True) -> Page:
        """
        Given the ID of the context menu, it will dismiss the menu.

        For example, the tab context menu corresponds to the id of tabContextMenu. Usage would be: tabs.hide_popup("tabContextMenu")
        """
        script = f'document.querySelector("#{context_menu}").hidePopup();'
        if chrome:
            with self.driver.context(self.driver.CONTEXT_CHROME):
                self.driver.execute_script(script)
        else:
            with self.driver.context(self.driver.CONTEXT_CONTENT):
                self.driver.execute_script(script)

    def hide_popup_by_class(self, class_name: str, retry=False) -> None:
        """
        Given the class name of the context menu, it will dismiss the menu.

        For example, if the context menu corresponds to the class name of 'context-menu',
        usage would be: tabs.hide_popup_by_class("context-menu")
        """
        try:
            with self.driver.context(self.context_id):
                script = f"""var element = document.querySelector(".{class_name}");
                         if (element && element.hidePopup) {{
                             element.hidePopup();
                         }}
                        """
                self.driver.execute_script(script)
        except NoSuchWindowException:
            if not retry:
                with self.driver.context(self.opposite_context()):
                    self.hide_popup_by_class(class_name, True)
            else:
                raise NoSuchWindowException

    def handle_os_download_confirmation(self, keyboard: Controller, sys_platform: str):
        """
        This function handles the keyboard shortcuts. If on Linux, it simulates switching
        to OK. On other platforms, it directly presses enter.
        """
        if sys_platform == "Linux":
            # Perform the series of ALT+TAB key presses on Linux
            keyboard.press(Key.alt)
            keyboard.press(Key.tab)
            keyboard.release(Key.tab)
            keyboard.release(Key.alt)
            time.sleep(1)
            keyboard.press(Key.alt)
            keyboard.press(Key.tab)
            keyboard.release(Key.tab)
            keyboard.release(Key.alt)
            time.sleep(1)
            keyboard.press(Key.tab)
            keyboard.release(Key.tab)
            time.sleep(1)
            keyboard.press(Key.tab)
            keyboard.release(Key.tab)

        # Press enter to confirm the download on all platforms
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)

    def hide_popup_by_child_node(
        self, reference: Union[str, tuple, WebElement], labels=[], retry=False
    ) -> Page:
        try:
            with self.driver.context(self.context_id):
                logging.info("hide popup child: start")
                node = self.fetch(reference, labels=labels)
                logging.info("hide popup child: fetched")
                script = """var element = arguments[0].parentNode;
                         if (element && element.hidePopup) {
                            element.hidePopup();
                         }"""
                self.driver.execute_script(script, node)
        except NoSuchWindowException:
            if not retry:
                with self.driver.context(self.opposite_context()):
                    self.hide_popup_by_child_node(reference, labels, True)
            else:
                raise NoSuchWindowException

    def get_localstorage_item(self, key: str):
        return self.driver.execute_script(f"return window.localStorage.getItem({key});")

    def _get_alert(self):
        try:
            alert = self.driver.switch_to.alert
        except NoAlertPresentException:
            return False
        return alert

    def get_alert(self):
        alert = self.wait.until(lambda _: self._get_alert())
        return alert

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

    def get_css_zoom(self):
        """
        Checks the CSS zoom and transform scale to determine the current zoom level.
        """
        # Retrieve the CSS zoom property on the body element
        css_zoom = self.driver.execute_script(
            "return window.getComputedStyle(document.body).zoom"
        )
        if css_zoom:
            return float(css_zoom)

        # If zoom property is not explicitly set, check the transform scale
        css_transform_scale = self.driver.execute_script("""
            const transform = window.getComputedStyle(document.body).transform;
            if (transform && transform !== 'none') {
                return transform;
            } else {
                return null;
        """)

        # Parse the transform matrix to extract the scale factor (e.g., matrix(a, b, c, d, e, f))
        if css_transform_scale:
            scale_factor = float(css_transform_scale.split("(")[1].split(",")[0])
            return scale_factor

        # Default return if neither zoom nor transform is set
        return 1.0
