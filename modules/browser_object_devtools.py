from selenium.webdriver.remote.webelement import WebElement

from modules.page_base import BasePage


class Devtools(BasePage):
    URL_TEMPLATE = ""

    def check_opened(self) -> BasePage:
        self.wait_for_page_to_load()
        return self
