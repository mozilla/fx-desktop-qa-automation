from typing import Union

from selenium.webdriver.remote.webelement import WebElement

from modules.page_base import BasePage


class ContextMenu(BasePage):
    """
    Browser Object Model (base class/parent class) for the context menus upon right clicking
    """

    URL_TEMPLATE = ""

    def click_context_item(
        self, reference: Union[str, tuple, WebElement], labels=[]
    ) -> BasePage:
        """
        Clicks the context item.
        """
        with self.driver.context(self.driver.CONTEXT_CHROME):
            item = self.fetch(reference, labels=labels)
            item.click()
            self.hide_popup_by_child_node(item)
            return self
