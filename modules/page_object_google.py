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

    def select_num_columns(self, n: int) -> GenericPage:
        """Select n columns starting from the current position"""
        self.actions.key_down(Keys.CONTROL)
        self.actions.send_keys(Keys.SPACE)
        self.actions.key_up(Keys.CONTROL).perform()
        self.actions.key_down(Keys.SHIFT)
        for _ in range(n - 1):
            self.actions.send_keys(Keys.RIGHT)
        self.actions.key_up(Keys.SHIFT).perform()
        return self
    
    def select_entire_table(self) -> GenericPage:
        """Select the entire table starting from the current position"""
        mod_key = Keys.COMMAND if self.sys_platform else Keys.CONTROL
        self.actions.key_down(mod_key)
        self.actions.key_down(Keys.SHIFT)
        self.actions.send_keys(Keys.SPACE)
        self.actions.key_up(Keys.SHIFT)
        self.actions.key_up(mod_key).perform()
        return self

    def go_to_top_left_cell(self) -> GenericPage:
        """Select cell A1 (top left)"""
        if self.sys_platform == "Darwin":
            self.actions.key_down(Keys.COMMAND)
            self.actions.send_keys(Keys.LEFT)
            self.actions.send_keys(Keys.UP)
            self.actions.send_keys(Keys.UP)
        else:
            self.actions.key_down(Keys.CONTROL)
            self.actions.send_keys(Keys.HOME)
        return self
