from selenium.webdriver import ActionChains

from modules.page_base import BasePage


class MenuBar(BasePage):
    """Page Object Model for Menu Bar navigation"""

    def activate_menu_bar(self) -> BasePage:
        """Enables the Menu Bar at the top of the window (if needed)"""
        if self.sys_platform() != "Darwin":
            with self.driver.context(self.driver.CONTEXT_CHROME):
                element = self.get_element("toolbar-blank-space")
                actions = ActionChains(self.driver)
                actions.context_click(element).perform()
                self.get_element("menu-bar-checkbox").click()
        return self

    def open_menu(self, menu_name: str) -> BasePage:
        """Opens a specified menu from the Menu Bar"""
        self.activate_menu_bar()
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.get_element(f"{menu_name.lower()}-menu-button").click()
        return self
