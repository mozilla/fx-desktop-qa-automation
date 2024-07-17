from typing import Union

from selenium.webdriver.remote.webelement import WebElement

from modules.page_base import BasePage


class ContextMenu(BasePage):
    """
    Browser Object Model (base class/parent class) for the context menus upon right clicking
    """

    URL_TEMPLATE = ""

    def get_context_item(self, item: str) -> WebElement:
        """
        Gets the context menu item from the context menu
        """
        with self.driver.context(self.driver.CONTEXT_CHROME):
            return self.get_element(item)

    def click_context_item(
        self, reference: Union[str, tuple, WebElement], labels=[]
    ) -> BasePage:
        """
        Clicks the context item.
        """
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.fetch(reference, labels=labels).click()
            return self

    def click_and_hide(
        self, reference: Union[str, tuple, WebElement], labels=[]
    ) -> BasePage:
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.fetch(reference, labels=labels).click()
            self.hide_popup_by_child_node(reference, labels=labels)
            return self
