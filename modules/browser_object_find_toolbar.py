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

    def previous_match(self) -> BasePage:
        """Click the Previous Match button"""
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.get_element("previous-match-button").click()
