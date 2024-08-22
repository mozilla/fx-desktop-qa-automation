from typing import Union

from selenium.webdriver.remote.webelement import WebElement

from modules.browser_object_context_menu import ContextMenu
from modules.page_base import BasePage


class CustomizeFirefox(BasePage):
    """
    POM for customize Firefox page
    """

    URL_TEMPLATE = ""

    def add_widget_to_toolbar(
        self, reference: Union[str, tuple, WebElement], labels=[]
    ) -> BasePage:
        with self.driver.context(self.driver.CONTEXT_CHROME):
            widget = self.fetch(reference, labels=labels)
            self.context_click(widget)
            ContextMenu(self.driver).click_and_hide_menu(
                "customize-firefox-add-toolbar"
            )
        return self
