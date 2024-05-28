import logging
from typing import Union

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

from modules.page_base import BasePage


class TabBar(BasePage):
    """Page Object Model for tab navigation"""

    URL_TEMPLATE = "about:blank"

    class MediaStatus:
        """Fake enum: just return a string based on a constant name"""

        def __init__(self):
            self.PLAYING = "playing"
            self.MUTED = "muted"
            self.AUTOPLAY_BLOCKED = "blocked"
            self.PIP = "pip"

    MEDIA_STATUS = MediaStatus()

    def new_tab_by_button(self) -> BasePage:
        """Use the New Tab button (+) to open a new tab"""
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.get_element("newtab-button").click()
        return self

    def click_tab_by_title(self, title: str) -> BasePage:
        """Given a full page title, click the corresponding tab"""
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.get_element("tab-by-title", labels=[title]).click()
        return self

    def click_tab_by_index(self, index: int) -> BasePage:
        """Given a tab index (int), click the corresponding tab"""
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.get_element("tab-by-index", labels=[str(index)]).click()
        return self

    def get_tab(self, identifier: Union[str, int]) -> Union[WebElement, None]:
        """Return a tab root based on either a title or an index"""
        with self.driver.context(self.driver.CONTEXT_CHROME):
            if isinstance(identifier, int):
                tab = self.get_element("tab-by-index", labels=[str(identifier)])
            elif isinstance(identifier, str):
                tab = self.get_element("tab-by-title", labels=[identifier])
            else:
                # if we get an unexpected type, we shouldn't assume that the user wants sys exit
                # but we have to cause problems for them nonetheless
                assert False
                tab = None
            return tab

    def click_tab_mute_button(self, identifier: Union[str, int]) -> BasePage:
        """Click the tab icon overlay, no matter what's happening with media"""
        logging.info(f"toggling tab mute for {identifier}")
        tab = self.get_tab(identifier)
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.actions.move_to_element(tab).perform()
            self.get_element("tab-icon-overlay").click()
        return self

    def expect_tab_sound_status(
        self, identifier: Union[str, int], status: MediaStatus
    ) -> BasePage:
        """Check to see if the tab has an expected MediaStatus"""
        tab = self.get_tab(identifier)
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.actions.move_to_element(tab).perform()
            self.expect(
                EC.visibility_of(self.get_element("tab-sound-label", labels=[status]))
            )
        return self
