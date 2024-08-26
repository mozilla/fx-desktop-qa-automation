import subprocess

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
        """Opens a specified menu from the Menu Bar based on the OS"""
        if self.sys_platform() == "Darwin":
            self._open_menu_mac(menu_name)
        else:
            self.activate_menu_bar()
            with self.driver.context(self.driver.CONTEXT_CHROME):
                self.get_element(f"{menu_name.lower()}-menu-button").click()
        return self

    def _open_menu_mac(self, menu_name: str):
        """Uses AppleScript to open a specified menu on macOS since Menu Bar is a mac native specific UI element"""
        script = f"""
        tell application "System Events"
            tell process "Firefox"
                set frontmost to true
                click menu bar item "{menu_name}" of menu bar 1
            end tell
        end tell
        """
        subprocess.run(["osascript", "-e", script], check=True)

    def check_menu_item_apple_script(self, menu_name: str, menu_item_name: str) -> bool:
        """Uses AppleScript to check if a specific menu item is present and visible in the specified menu."""
        script = f"""
        tell application "System Events"
            tell process "Firefox"
                set menu_item_exists to exists menu item "{menu_item_name}" of menu "{menu_name}" of menu bar 1
                return menu_item_exists
            end tell
        end tell
        """
        result = subprocess.run(
            ["osascript", "-e", script], capture_output=True, text=True
        )
        return result.stdout.strip() == "true"
