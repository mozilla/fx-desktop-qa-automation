from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement

from modules.page_base import BasePage
from modules.page_object import GenericPage


class GoogleSearch(BasePage):
    """
    Page Object Model for the google.com page
    """

    URL_TEMPLATE = "https://www.google.com/"

    def type_in_search_bar(self, text: str) -> BasePage:
        """
        Sends text into the search bar
        """
        search_bar = self.get_search_bar_element()
        search_bar.send_keys(text)

    def press_enter_search_bar(self) -> BasePage:
        """
        Sends Enter into the search bar
        """
        search_bar = self.get_search_bar_element()
        search_bar.send_keys(Keys.ENTER)

    def get_search_bar_element(self) -> WebElement:
        """
        Finds the search bar element and returns it as a WebElement
        """
        return self.get_element("search-bar-textarea")


class GoogleSheets(GenericPage):
    """
    Page Object Model for the docs.google.com/spreadsheets page
    """

    def open_insert_menu(self) -> GenericPage:
        """Open the insert menu"""
        self.click_on("insert-button")
        return self

    def select_num_rows(self, n: int) -> GenericPage:
        """Select n rows starting from the current position"""
        self.actions.key_down(Keys.SHIFT)
        self.actions.send_keys(Keys.SPACE)
        for _ in range(n-1):
            self.actions.send_keys(Keys.ARROW_DOWN)
        self.actions.key_up(Keys.SHIFT).perform()
        return self

    def cycle_to_next_sheet(self, sys_platform) -> GenericPage:
        """Cycle to the sheet on the right (loops to the first if the end is reached)"""
        mod_key = Keys.ALT if sys_platform == "Darwin" else "\u2325" # Option Key
        self.actions.key_down(mod_key)
        self.actions.send_keys(Keys.ARROW_DOWN)
        self.actions.key_up(mod_key).perform()
        return self
