import json
import logging

from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from modules.browser_object_panel_ui import PanelUi
from modules.page_base import BasePage


class FindToolbar(BasePage):
    URL_TEMPLATE = ""

    def __init__(self, driver: Firefox, **kwargs):
        super().__init__(driver, **kwargs)
        self.panel_ui = PanelUi(self.driver)
        self.match_dict = {}

    @BasePage.context_chrome
    def open(self) -> BasePage:
        """Use PanelUi to open the Find Toolbar, wait for element to load"""
        self.panel_ui.open_panel_menu()
        self.panel_ui.select_panel_setting("find-in-page")
        self.wait_for_page_to_load()
        return self

    @BasePage.context_chrome
    def open_with_key_combo(self) -> BasePage:
        """Use Cmd/Ctrl + F to open the Find Toolbar, wait for load"""
        if self.sys_platform() == "Darwin":
            mod_key = Keys.COMMAND
        else:
            mod_key = Keys.CONTROL
        self.perform_key_combo(mod_key, "f")
        self.wait_for_page_to_load()
        return self

    @BasePage.context_chrome
    def find(self, term: str) -> BasePage:
        """Use the Find Toolbar to search"""
        find_bar = self.get_element("find-toolbar-input")
        find_bar.click()
        find_bar.clear()
        find_bar.send_keys(term + Keys.ENTER)
        if find_bar.get_property("status") != "notfound":
            self.match_dict = self.get_match_args()
        return self

    @BasePage.context_chrome
    def get_match_args(self) -> dict:
        """Return the status of the find session"""
        self.expect(
            EC.text_to_be_present_in_element_attribute(
                self.get_selector("matches-label"), "data-l10n-args", ":"
            )
        )
        matches = self.get_element("matches-label")
        logging.info(matches.get_attribute("outerHTML"))
        match_status_str = matches.get_attribute("data-l10n-args")
        self.match_dict = json.loads(match_status_str)
        return self.match_dict

    @BasePage.context_chrome
    def next_match(self) -> BasePage:
        """Click the Next Match button"""
        self.get_element("next-match-button").click()
        if self.match_dict["current"] < self.match_dict["total"]:
            self.match_dict["current"] += 1
        else:
            self.match_dict["current"] = 1
        return self

    @BasePage.context_chrome
    def previous_match(self) -> BasePage:
        """Click the Previous Match button"""
        self.get_element("previous-match-button").click()
        if self.match_dict["current"] > 1:
            self.match_dict["current"] -= 1
        else:
            self.match_dict["current"] = self.match_dict["total"]
        return self

    @BasePage.context_chrome
    def rewind_to_first_match(self) -> BasePage:
        """Go back to match 1 of n"""
        while self.match_dict["current"] != 1:
            self.previous_match()
        return self

    @BasePage.context_chrome
    def navigate_matches_by_keys(self, backwards=False) -> BasePage:
        """Use F3 and Shift+F3 to navigate matches"""
        if backwards:
            self.perform_key_combo(Keys.SHIFT, Keys.F3)
        else:
            logging.info(f"sending {Keys.F3.encode()}")
            self.actions.send_keys(Keys.F3).perform()
        return self

    @BasePage.context_chrome
    def navigate_matches_n_times(self, n: int):
        for _ in range(n):
            self.next_match()
