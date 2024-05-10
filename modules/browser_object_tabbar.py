import logging
from typing import Union

from selenium.webdriver.support import expected_conditions as EC

from modules.page_base import BasePage


class TabBar(BasePage):
    """Page Object Model for tab navigation"""

    URL_TEMPLATE = "about:blank"

    def new_tab_by_button(self) -> BasePage:
        """Use the New Tab button (+) to open a new tab"""
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.get_element("newtab-button").click()
        return self


    def click_tab_by_title(self, title: str) -> BasePage:
        """Given a full page title, click the corresponding tab"""
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.get_element("tab-by-title", title).click()
        return self

    def click_tab_by_index(self, index: int) -> BasePage:
        """Given a tab index (int), click the corresponding tab"""
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.get_element("tab-by-index", str(index)).click()
        return self

    def toggle_tab_mute(self, identifier: Union[str, int], assert_current=None) -> BasePage:
        """
        Given a tab title or index, mute or unmute that tab. Optionally, assert that
        the tab is in a given media state first.
        """
        with self.driver.context(self.driver.CONTEXT_CHROME):
            if assert_current is not None:
                assert EC.visibility_of(self.get_element("tab-sound-label", assert_current))
            is_playing = EC.visibility_of(self.get_element("tab-sound-label", "playing"))
            if not is_playing:
                assert EC.visibility_of(self.get_element("tab-sound-label", "muted"))
            if isinstance(identifier, int):
                tab = self.get_element("tab-by-index", str(identifier))
            elif isinstance(identifier, str):
                tab = self.get_element("tab-by-title", identifier)
            else:
                # if we get an unexpected type, we shouldn't assume that the user wants sys exit
                # but we have to cause problems for them nonetheless
                assert False
                return self
            self.actions.move_to_element(tab).perform()
            assert EC.visibility_of(self.get_element("tab-sound-label", "playing"))
            self.get_element("tab-icon-overlay").click()
            self.wait.until(EC.visibility_of(self.get_element("tab-sound-label", "muted")))
            return self
