from typing import Union

from selenium.webdriver.remote.webelement import WebElement

from modules.browser_object_context_menu import ContextMenu
from modules.page_base import BasePage


class CustomizeFirefox(BasePage):
    """
    POM for customize Firefox page
    """

    URL_TEMPLATE = ""

    @BasePage.context_chrome
    def add_widget_to_toolbar(
        self, reference: Union[str, tuple, WebElement], labels=[]
    ) -> BasePage:
        widget = self.fetch(reference, labels=labels)
        self.context_click(widget)
        ContextMenu(self.driver).click_and_hide_menu("customize-firefox-add-toolbar")
        self.element_clickable("nav-searchbar")
        self.click_on("done-button")
        return self

    @BasePage.context_chrome
    def remove_widget_from_toolbar(
        self, reference: Union[str, tuple, WebElement], labels=[]
    ) -> BasePage:
        """Right-click on the widget and click on "Remove from toolbar" in the context menu."""
        widget = self.fetch(reference, labels=labels)
        self.context_click(widget)
        ContextMenu(self.driver).click_and_hide_menu(
            "customize-widget-remove-from-toolbar"
        )
        return self

    @BasePage.context_chrome
    def restore_defaults(self) -> BasePage:
        """Click on the Restore Defaults button"""
        self.click_on("restore-defaults-button")
        return self

    @BasePage.context_chrome
    def submit_the_changes_via_done_button(self) -> BasePage:
        """Click on the Done button"""
        self.click_on("done-button")
        return self
