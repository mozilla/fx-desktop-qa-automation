from selenium.webdriver.remote.webelement import WebElement

from modules.page_base import BasePage


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

    def get_search_bar_element(self) -> WebElement:
        """
        Finds the search bar element and returns it as a WebElement
        """
        return self.get_element("search-bar-textarea")
