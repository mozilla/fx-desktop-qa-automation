from time import sleep

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from modules.browser_object_panel_ui import PanelUi
from modules.page_base import BasePage
from modules.util import BrowserActions


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

    def switch_to_preview_window(self) -> BasePage:
        """Switch to the iframe holding the Print Preview"""
        ba = BrowserActions(self.driver)
        sleep(3)
        with self.driver.context(self.driver.CONTEXT_CHROME):
            ba.switch_to_iframe_context(self.get_element("print-settings-browser"))
            self.expect(
                lambda _: self.driver.execute_script(
                    'return document.readyState === "complete";'
                )
            )
        return self

    def start_print(self, secondary_confirm=True) -> BasePage:
        """Press Enter in Print"""
        self.switch_to_preview_window()
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.actions.send_keys_to_element(self.get_element("print-settings-browser"), Keys.TAB + Keys.ENTER).perform()
            self.
            self.switch_to_new_window()
            self.actions.send_keys(Keys.ENTER).perform()
        return self

    def select_print_to_pdf(self) -> BasePage:
        """Select Print to PDF"""
        from pynput import Controller, Key

        keyboard = Controller()

        self.switch_to_preview_window()
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.actions.send_keys_to_element(
                self.get_element("print-settings-browser"), Keys.TAB
            )
        return self
