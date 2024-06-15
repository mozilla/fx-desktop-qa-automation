from selenium.webdriver.common.keys import Keys

from modules.browser_object import PanelUi
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
