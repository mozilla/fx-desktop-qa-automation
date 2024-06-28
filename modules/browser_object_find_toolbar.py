import json
import logging

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from modules.browser_object_panel_ui import PanelUi
from modules.page_base import BasePage


class FindToolbar(BasePage):
    URL_TEMPLATE = ""

    def open(self) -> BasePage:
        """Use PanelUi to open the Find Toolbar, wait for element to load"""
        panel_ui = PanelUi(self.driver)
        with self.driver.context(self.driver.CONTEXT_CHROME):
            panel_ui.open_panel_menu()
            panel_ui.select_panel_setting("find-in-page")
            self.wait_for_page_to_load()
        return self

    def open_with_key_combo(self) -> BasePage:
        """Use Cmd/Ctrl + F to open the Find Toolbar, wait for load"""
        with self.driver.context(self.driver.CONTEXT_CHROME):
            if self.sys_platform() == "Darwin":
                mod_key = Keys.COMMAND
            else:
                mod_key = Keys.CONTROL
            self.perform_key_combo(mod_key, "f")
            self.wait_for_page_to_load()
        return self

    def find(self, term: str) -> BasePage:
        """Use the Find Toolbar to search"""
        with self.driver.context(self.driver.CONTEXT_CHROME):
            findbar = self.get_element("find-toolbar-input")
            findbar.click()
            findbar.clear()
            findbar.send_keys(term + Keys.ENTER)
        return self

    def get_match_args(self) -> dict:
        """Return the status of the find session"""
        with self.driver.context(self.driver.CONTEXT_CHROME):
            matches = self.get_element("matches-label")
            self.expect(
                EC.text_to_be_present_in_element_attribute(
                    self.get_selector("matches-label"), "data-l10n-args", ":"
                )
            )
            logging.info(matches.get_attribute("outerHTML"))
            match_status_str = matches.get_attribute("data-l10n-args")
            return json.loads(match_status_str)

    def next_match(self) -> BasePage:
        """Click the Next Match button"""
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.get_element("next-match-button").click()
        return self

    def previous_match(self) -> BasePage:
        """Click the Previous Match button"""
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.get_element("previous-match-button").click()
        return self

    def rewind_to_first_match(self) -> BasePage:
        """Go back to match 1 of n"""
        with self.driver.context(self.driver.CONTEXT_CHROME):
            position = self.get_match_args()["current"]
            total = self.get_match_args()["total"]
            while position != 1:
                if position < total // 2:
                    self.previous_match()
                else:
                    self.next_match()
                position = self.get_match_args()["current"]
        return self

    def navigate_matches_by_keys(self, backwards=False) -> BasePage:
        """Use F3 and Shift+F3 to navigate matches"""
        with self.driver.context(self.driver.CONTEXT_CHROME):
            if backwards:
                self.perform_key_combo(Keys.SHIFT, Keys.F3)
            else:
                logging.info(f"sending {Keys.F3.encode()}")
                self.actions.send_keys(Keys.F3).perform()
            return self
