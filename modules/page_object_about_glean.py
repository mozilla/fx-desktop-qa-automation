from time import sleep

from pypom import Page, Region
from selenium.common.exceptions import (
    InvalidArgumentException,
    WebDriverException,
)
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

from modules.page_base import BasePage
from modules.util import BrowserActions


class AboutGlean(BasePage):
    """Page Object Model for about:glean"""

    URL_TEMPLATE = "about:glean"

    def change_ping_id(self, ping_id: str):
        ba = BrowserActions(self.driver)
        ping_input = self.get_element("ping-id-input")
        ba.clear_and_fill(ping_input, ping_id)
        self.wait.until(
            EC.text_to_be_present_in_element(
                self.get_selector("ping-submit-label"), ping_id
            )
        )
        self.get_element("ping-submit-button").click()
        return self
