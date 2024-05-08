import logging
from collections.abc import Iterable
from random import shuffle
from typing import Union

from selenium.common.exceptions import (
    InvalidArgumentException,
    WebDriverException,
)
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.shadowroot import ShadowRoot
from selenium.webdriver.remote.webelement import WebElement


class Utilities:
    """
    Methods that may be useful, that have nothing to do with Selenium.
    """

    def __init__(self):
        pass

    def random_string(self, n: int) -> str:
        """A random string of n alphanum characters, including possible hyphen."""
        chars = list("bdehjlmptvwxz2678-BDEHJLMPTVWXZ")
        shuffle(chars)
        return "".join(chars[:n])


class BrowserActions:
    """
    Shortcut methods for things that are unsightly in Selenium-Python.

    ...

    Attributes
    ----------
    driver : selenium.webdriver.Firefox
        The instance of WebDriver under test.
    """

    def __init__(self, driver: Firefox):
        self.driver = driver

    def clear_and_fill_no_additional_keystroke(self, webelement: WebElement, term: str):
        """
        Given a WebElement, send it the string `term` with no additional keystrokes.

        ...

        Parameters
        ----------
        webelement : selenium.webdriver.remote.webelement.WebElement
        term : str
            The string to send to this element
        """
        webelement.clear()
        webelement.send_keys(term)

    def clear_and_fill(self, webelement: WebElement, term: str):
        """
        Given a WebElement, send it the string `term` to it followed by Keys.RETURN.

        ...

        Parameters
        ----------
        webelement : selenium.webdriver.remote.webelement.WebElement
        term : str
            The string to send to this element
        """
        webelement.clear()
        webelement.send_keys(term, Keys.RETURN)

    def find_clear_and_fill(self, element_tuple: Iterable, term: str):
        """
        Given a Tuple of (By.CONSTANT, str), select the first matching element
        and send the string `term` to it followed by Keys.RETURN.

        ...

        Parameters
        ----------
        element_tuple : Tuple[selenium.webdriver.common.by.By.CONSTANT, str]
            The tuple used in e.g. expected_conditions methods to select an element
        term : str
            The string to send to this element
        """
        webelement = self.driver.find_element(*element_tuple)
        self.clear_and_fill(webelement, term)

    def search(self, term: str, with_enter=True):
        """
        Type something into the Awesome Bar. By default, press Enter.
        """
        with self.driver.context(self.driver.CONTEXT_CHROME):
            url_bar = self.driver.find_element(By.ID, "urlbar-input")
            url_bar.clear()
            if with_enter:
                url_bar.send_keys(term, Keys.RETURN)
            else:
                url_bar.send_keys(term)

    def filter_elements_by_attr(
        self, elements: list[WebElement], attr: str, value: str
    ) -> list[WebElement]:
        """
        Given a list of WebElements, return the ones where attribute `attr` has value `value`.
        """
        return [el for el in elements if el.get_attribute(attr) == value]

    def pick_element_from_list_by_text(
        self, elements: list[WebElement], substr: str
    ) -> WebElement:
        """
        Given a list of WebElements, return the one where innerText matches `substr`.
        Return None if no matches. Raise RuntimeError if more than one matches.
        """
        matches = [el for el in elements if substr in el.get_attribute("innerText")]
        if len(matches) == 1:
            return matches[0]
        elif len(matches) == 0:
            return None
        else:
            raise RuntimeError("More than one element matches text.")


class PomUtils:
    """
    Shortcut methods for POM and BOM related activities.

    ...

    Attributes
    ----------
    driver : selenium.webdriver.Firefox
        The instance of WebDriver under test.
    """

    def __init__(self, driver: Firefox):
        self.driver = driver

    def get_shadow_content(
        self, element: WebElement
    ) -> list[Union[WebElement, ShadowRoot]]:
        """
        Given a WebElement, return the shadow DOM root or roots attached to it. Returns a list.
        """
        logging.info(f"Getting shadow nodes from root {element}")

        def shadow_from_script():
            shadow_children = self.driver.execute_script(
                "return arguments[0].shadowRoot.children", element
            )
            if len(shadow_children) and any(shadow_children):
                logging.info("Returning script-returned shadow elements")
                shadow_elements = [s for s in shadow_children if s is not None]
                logging.info(shadow_elements)
                return shadow_elements

        try:
            logging.info("Getting shadow content...")
            shadow_root = element.shadow_root
            shadow_content = [shadow_root]
            if not shadow_content:
                logging.info("Selenium shadow nav returned no elements in Shadow DOM")
                return shadow_from_script()
            return shadow_content
        except InvalidArgumentException:
            logging.info("Selenium shadow nav failed.")
            return shadow_from_script()
        return []

    def css_selector_matches_element(
        self, element: Union[WebElement, ShadowRoot], selector: list
    ) -> bool:
        if type(element) == ShadowRoot:
            return False
        sel = f'"{selector[1]}"'
        return self.driver.execute_script(
            f"return arguments[0].matches({sel})", element
        )

    def find_shadow_element(
        self, shadow_parent: Union[WebElement, ShadowRoot], selector: list
    ) -> WebElement:
        """
        Given a WebElement with a shadow root attached, find a selector in the
        shadow DOM of that root.
        """
        original_timeout = self.driver.timeouts.implicit_wait
        matches = []
        logging.info(f"Requesting shadow nodes from root {shadow_parent}...")
        shadow_nodes = self.get_shadow_content(shadow_parent)
        logging.info(f"Found {len(shadow_nodes)} shadow nodes...")
        logging.info(f"Looking for {selector}...")
        self.driver.implicitly_wait(0)
        for node in shadow_nodes:
            if self.css_selector_matches_element(node, selector):
                # If we collect shadow children via JS, and one matches the selector, we're good.
                self.driver.implicitly_wait(original_timeout)
                return node
            elements = node.find_elements(*selector)
            if elements:
                logging.info("Found a match")
                matches.extend(elements)
        self.driver.implicitly_wait(original_timeout)
        if len(matches) == 1:
            logging.info("Returning match...")
            return matches[0]
        elif len(matches):
            raise WebDriverException(
                "More than one element matched within a Shadow DOM"
            )
        else:
            logging.info("No matches found.")
            return None
