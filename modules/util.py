from collections.abc import Iterable
from random import shuffle

from selenium.common.exceptions import (
    InvalidArgumentException,
    WebDriverException,
)
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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
    Shorcut methods for things that are unsightly in Selenium-Python.

    ...

    Attributes
    ----------
    driver : selenium.webdriver.Firefox
        The instance of WebDriver under test.
    """

    def __init__(self, driver: Firefox):
        self.driver = driver

    def clear_and_fill(self, webelement: WebElement, term: str):
        """
        Given a WebElement, send it the string `term` to it followed by Keys.RETURN.

        ...

        Attributes
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

        Attributes
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
        """docstring"""
        return [el for el in elements if e.get_attribute(attr) == value]

    def pick_element_from_list_by_text(
        self, elements: list[WebElement], substr: str
    ) -> WebElement:
        """docstring"""
        matches = [el for el in elements if substr in e.get_attribute("innerText")]
        if len(matches) == 1:
            return matches[0]
        elif len(matches) == 0:
            return None
        else:
            raise RuntimeError("More than one element matches text.")


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
