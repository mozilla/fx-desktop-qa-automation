from selenium.webdriver import ActionChains

from modules.page_base import BasePage


class MenuBar(BasePage):
    """Page Object Model for Menu Bar navigation"""

    URL_TEMPLATE = ""

    def activate_menu_bar(self):
        """Enables the Menu Bar at the top of the window"""
        with self.driver.context(self.driver.CONTEXT_CHROME):
            element = self.get_element("toolbar-blank-space")
            actions = ActionChains(self.driver)
            actions.context_click(element).perform()
            self.get_element("menu-bar-checkbox").click()
        return self

    def open_history_menu(self) -> BasePage:
        """Opens History menu from Menu Bar"""
        self.activate_menu_bar()
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.get_element("history-menu-button").click()
        return self
