from pypom import Page, Region
from modules.page_base import BasePage
from selenium.common.exceptions import (
    InvalidArgumentException,
    WebDriverException,
)
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

from modules.util import BrowserActions


class AboutGlean(BasePage):
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
