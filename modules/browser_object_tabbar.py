import logging
from typing import Union

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
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

    class ScrollDirection:
        """Fake enum: Which way are we scrolling tabs"""

        def __init__(self):
            self.LEFT = "left"
            self.RIGHT = "right"

    SCROLL_DIRECTION = ScrollDirection()

    def new_tab_by_button(self) -> BasePage:
        """Use the New Tab button (+) to open a new tab"""
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.get_element("newtab-button").click()
        return self

    def new_tab_by_keys(self, sys_platform: str) -> BasePage:
        """Use keyboard shortcut to open a new tab"""
        if sys_platform == "Darwin":
            self.actions.key_down(Keys.COMMAND).send_keys("t").key_up(
                Keys.COMMAND
            ).perform()
        else:
            self.actions.key_down(Keys.CONTROL).send_keys("t").key_up(
                Keys.CONTROL
            ).perform()
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

    def get_tab_title(self, tab_element: WebElement) -> str:
        """Given a tab root element, get the title text of the tab"""
        with self.driver.context(self.driver.CONTEXT_CHROME):
            tab_label = tab_element.find_element(*self.get_selector("tab-title"))
            return tab_label.text

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

    def open_all_tabs_list(self) -> BasePage:
        """Click the Tab Visibility / List All Tabs button"""
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.get_element("list-all-tabs-button").click()
            self.expect(
                EC.text_to_be_present_in_element_attribute(
                    self.get_selector("list-all-tabs-button"), "open", "true"
                )
            )
        return self

    def count_tabs_in_all_tabs_menu(self) -> int:
        """Return the number of entries in the all tabs menu"""
        with self.driver.context(self.driver.CONTEXT_CHROME):
            all_tabs_menu = self.get_element("all-tabs-menu")
            all_tabs_entries = all_tabs_menu.find_elements(
                self.get_selector("all-tabs-entry")
            )
        return len(all_tabs_entries)

    def scroll_tabs(self, direction: ScrollDirection) -> BasePage:
        """Scroll tabs in tab bar using the < and > scroll buttons"""
        logging.info(f"Scrolling tabs {direction}")
        with self.driver.context(self.driver.CONTEXT_CHROME):
            try:
                scroll_button = self.get_element(f"tab-scrollbox-{direction}-button")
                scroll_button.click()
            except NoSuchElementException:
                logging.info("Could not scroll any further!")
        return self

    def get_text_of_all_tabs_entry(self, selected=False, index=0) -> str:
        """
        Given an index or a True for the selected attr,
        get the text in the corresponding entry in the all tabs menu.

        ...

        Parameters
        ----------

        selected: bool
            Get the selected tab's text? Overrides index.

        index: int
            Index of List All Tabs menu entry to get text from

        Returns
        -------

        str: Text of List All Tabs menu entry.
        """
        entry = None
        if selected:
            entry = self.get_element("all-tabs-entry-selected")
        else:
            entries = self.get_elements("all-tabs-entry")
            entry = entries[index]
        return entry.find_element(By.CLASS_NAME, "all-tabs-button").get_attribute(
            "label"
        )

    def get_location_of_all_tabs_entry(self, selected=False, index=0) -> dict:
        """
        Given an index or a True for the selected attr,
        get the location of the entry in the all tabs menu.

        ...

        Parameters
        ----------

        selected: bool
            Get the selected tab's location? Overrides index.

        index: int
            Index of List All Tabs menu entry whose location we want.

        Returns
        -------

        dict: location of entry, keys are 'x' and 'y'.
        """
        entry = None
        if selected:
            entry = self.get_element("all-tabs-entry-selected")
        else:
            entries = self.get_elements("all-tabs-entry")
            entry = entries[index]
        return entry.find_element(By.CLASS_NAME, "all-tabs-button").location

    def scroll_on_all_tabs_menu(self, down=True, pixels=200) -> BasePage:
        """
        Scroll the List All Tabs menu down or up.

        ...

        Parameters
        ----------

        down: bool
            Should we scroll down? A value of False scrolls up.

        pixels: int
            The number of pixels to scroll the bar
        """
        with self.driver.context(self.driver.CONTEXT_CHROME):
            menu = self.get_element("all-tabs-menu")
            logging.info(f"menu location: {menu.location}")
            logging.info(f"menu size: {menu.size}")

            def get_bar_y():
                return min(
                    [
                        menu.size["height"] // 2,
                        self.driver.get_window_size()["height"] // 2,
                    ]
                )

            # HACK: Can't figure out what the scrollbox selector is, but it's ~4 pixels
            #  off the edge of the menu.
            x_start = menu.location["x"] + menu.size["width"] - 4
            # Grab the middle of the scrollbox area, most likely to hold the bar
            y_start = menu.location["y"] + get_bar_y()
            # +Y is down, -Y is up
            sign = 1 if down else -1
            self.actions.move_by_offset(x_start, y_start)
            self.actions.click_and_hold()
            self.actions.move_by_offset(0, (sign * pixels))
            self.actions.release()
            self.actions.perform()
