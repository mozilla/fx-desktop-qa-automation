from random import shuffle
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from collections.abc import Iterable


class Utilities:
    def __init__(self):
        pass

    def random_string(self, n: int) -> str:
        chars = list("bdehjlmptvwxz2678-BDEHJLMPTVWXZ")
        shuffle(chars)
        return "".join(chars[:n])


class BrowserActions:
    def __init__(self, driver: Firefox):
        self.driver = driver

    def find_clear_and_fill(self, element_tuple: Iterable, term: str):
        webelement = self.driver.find_element(*element_tuple)
        clear_and_fill(webelement, term)

    def clear_and_fill(self, webelement: WebElement, term: str):
        webelement.clear()
        webelement.send_keys(term, Keys.RETURN)

    def search(self, term: str):
        with self.driver.context(self.driver.CONTEXT_CHROME):
            url_bar = self.driver.find_element(By.ID, "urlbar-input")
            url_bar.clear()
            url_bar.send_keys(term, Keys.RETURN)

    def wait_on_title(self, substr: str):
        WebDriverWait(self.driver, 10).until(EC.title_contains(substr))

    def wait_on_element_contains_text(self, element_tuple: Iterable, substr: str):
        WebDriverWait(self.driver, 10).until(
            EC.text_to_be_present_in_element(element_tuple, substr)
        )
