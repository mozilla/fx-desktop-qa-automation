from modules.page_base import BasePage


class MenuBar(BasePage):
    """Page Object Model for Menu Bar navigation"""

    def activate_menu_bar(self) -> BasePage:
        """Enables the Menu Bar at the top of the window (if needed)"""
        if self.sys_platform() != "Darwin":
            with self.driver.context(self.driver.CONTEXT_CHROME):
                self.context_click("toolbar-blank-space")
                self.click_on("menu-bar-checkbox")
        return self

    def open_menu(self, menu_name: str) -> BasePage:
        """Opens a specified menu from the Menu Bar"""
        self.activate_menu_bar()
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.click_on(f"{menu_name.lower()}-menu-button")
        return self
