from selenium.webdriver.common.keys import Keys

from modules.browser_object_panel_ui import PanelUi
from modules.page_base import BasePage


class PrintPreview(BasePage):
    """Browser Object Model for Print Preview modal"""

    URL_TEMPLATE = "about:blank"

    def open(self) -> BasePage:
        """Use PanelUi to open the Print Preview, wait for element to load"""
        panel_ui = PanelUi(self.driver)
        with self.driver.context(self.driver.CONTEXT_CHROME):
            panel_ui.open_panel_menu()
            panel_ui.select_panel_setting("print-option")
            self.wait_for_page_to_load()
        return self

    def open_with_key_combo(self) -> BasePage:
        """Use Cmd/Ctrl + P to open the Print Preview, wait for load"""
        with self.driver.context(self.driver.CONTEXT_CHROME):
            if self.sys_platform() == "Darwin":
                mod_key = Keys.COMMAND
            else:
                mod_key = Keys.CONTROL
            self.perform_key_combo(mod_key, "p")
            self.wait_for_page_to_load()
        return self
