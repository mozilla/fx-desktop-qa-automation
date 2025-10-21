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
            self.PLAYING = "soundplaying"
            self.MUTED = "muted"
            self.AUTOPLAY_BLOCKED = "blocked"
            self.PIP = "pictureinpicture"

    MEDIA_STATUS = MediaStatus()

    class ScrollDirection:
        """Fake enum: Which way are we scrolling tabs"""

        def __init__(self):
            self.LEFT = "left"
            self.RIGHT = "right"

    SCROLL_DIRECTION = ScrollDirection()

    @BasePage.context_chrome
    def new_tab_by_button(self) -> BasePage:
        """Use the New Tab button (+) to open a new tab"""
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

    def new_window_by_keys(self, sys_platform: str) -> BasePage:
        """Use keyboard shortcut to open a new tab"""
        if sys_platform == "Darwin":
            self.actions.key_down(Keys.COMMAND).send_keys("n").key_up(
                Keys.COMMAND
            ).perform()
        else:
            self.actions.key_down(Keys.CONTROL).send_keys("n").key_up(
                Keys.CONTROL
            ).perform()
        return self

    def reopen_closed_tab_by_keys(self, sys_platform: str) -> BasePage:
        """Use keyboard shortcut to reopen a last closed tab"""
        if sys_platform == "Darwin":
            self.actions.key_down(Keys.COMMAND).key_down(Keys.SHIFT).send_keys(
                "t"
            ).key_up(Keys.SHIFT).key_up(Keys.COMMAND).perform()
        else:
            self.actions.key_down(Keys.CONTROL).key_down(Keys.SHIFT).send_keys(
                "t"
            ).key_up(Keys.SHIFT).key_up(Keys.CONTROL).perform()
        return self

    @BasePage.context_chrome
    def close_first_tab_by_icon(self) -> None:
        """Click the close icon on the first tab."""
        self.get_elements("tab-x-icon")[0].click()

    @BasePage.context_chrome
    def click_tab_by_title(self, title: str) -> BasePage:
        """Given a full page title, click the corresponding tab"""
        self.get_element("tab-by-title", labels=[title]).click()
        return self

    @BasePage.context_chrome
    def get_tab_by_title(self, title: str) -> WebElement:
        """Given a full page title, return the corresponding tab"""
        return self.get_element("tab-by-title", labels=[title])

    @BasePage.context_chrome
    def click_tab_by_index(self, index: int) -> BasePage:
        """Given a tab index (int), click the corresponding tab"""
        self.get_element("tab-by-index", labels=[str(index)]).click()
        return self

    @BasePage.context_chrome
    def get_tab(self, identifier: Union[str, int]) -> Union[WebElement, None]:
        """Return a tab root based on either a title or an index"""
        if isinstance(identifier, int):
            tab = self.get_element("tab-by-index", labels=[str(identifier)])
        elif isinstance(identifier, str):
            tab = self.get_element("tab-by-title", labels=[identifier])
        else:
            # if we get an unexpected type, we shouldn't assume that the user wants sys exit,
            # but we have to cause problems for them nonetheless
            assert False, "Error getting tab root"
        return tab

    @BasePage.context_chrome
    def is_pinned(self, tab_root: WebElement) -> bool:
        """Is this tab pinned?"""
        pinned = tab_root.get_attribute("pinned")
        if pinned in ["true", "false"]:
            return pinned == "true"
        else:
            assert False, "Error checking tab pinned status"

    @BasePage.context_chrome
    def click_tab_mute_button(self, identifier: Union[str, int]) -> BasePage:
        """Click the tab icon overlay, no matter what's happening with media"""
        logging.info(f"toggling tab mute for {identifier}")
        tab = self.get_tab(identifier)
        self.actions.move_to_element(tab).perform()
        self.get_element("tab-icon-overlay").click()
        return self

    @BasePage.context_chrome
    def get_tab_title(self, tab_element: WebElement) -> str:
        """Given a tab root element, get the title text of the tab"""
        tab_label = tab_element.find_element(*self.get_selector("tab-title"))
        return tab_label.text

    @BasePage.context_chrome
    def wait_for_tab_title(
        self, expected_title: str, tab_index: int = 1, timeout: int = 30
    ) -> None:
        """
        Wait until the tab title matches the expected value.
        Arguments:
            expected_title: The tab title to wait for.
            tab_index: The tab index to check (default is 1).
            timeout: Time limit (in seconds) before raising TimeoutException.
        """
        self.custom_wait(timeout=timeout).until(
            lambda d: self.get_tab_title(self.get_tab(tab_index)) == expected_title
        )

    @BasePage.context_chrome
    def expect_tab_sound_status(
        self, identifier: Union[str, int], status: MediaStatus
    ) -> BasePage:
        """
        Check to see if the tab has an expected MediaStatus
        """
        tab = self.get_tab(identifier)
        self.wait.until(lambda _: tab.get_attribute(status) is not None)
        return self

    def expect_title_contains(self, text: str) -> BasePage:
        """
        Check if the page title contains given text
        """
        self.expect(EC.title_contains(text))
        return self

    @BasePage.context_chrome
    def open_all_tabs_list(self) -> BasePage:
        """Click the Tab Visibility / List All Tabs button"""
        self.get_element("list-all-tabs-button").click()
        self.expect(
            EC.text_to_be_present_in_element_attribute(
                self.get_selector("list-all-tabs-button"), "open", "true"
            )
        )
        return self

    @BasePage.context_chrome
    def count_tabs_in_all_tabs_menu(self) -> int:
        """Return the number of entries in the all tabs menu"""
        all_tabs_menu = self.get_element("all-tabs-menu")
        all_tabs_entries = all_tabs_menu.find_elements(
            self.get_selector("all-tabs-entry")
        )
        return len(all_tabs_entries)

    @BasePage.context_chrome
    def scroll_tabs(self, direction: ScrollDirection) -> BasePage:
        """Scroll tabs in tab bar using the < and > scroll buttons"""
        logging.info(f"Scrolling tabs {direction}")
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

    @BasePage.context_chrome
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
        menu = self.get_element("all-tabs-menu")
        logging.info(f"menu location: {menu.location}")
        logging.info(f"menu size: {menu.size}")

        # HACK: Can't figure out what the scrollbox selector is, but it's ~4 pixels
        #  off the edge of the menu.
        x_start = (menu.size["width"] / 2.0) - 4.0
        # +Y is down, -Y is up
        sign = 1 if down else -1

        self.actions.move_to_element_with_offset(menu, x_start, 0)
        self.actions.click_and_hold()
        self.actions.move_by_offset(0, (sign * pixels))
        self.actions.release()
        self.actions.perform()

    @BasePage.context_chrome
    def close_tab(self, tab: WebElement) -> BasePage:
        """
        Given the index of the tab, it closes that tab.
        """
        # cur_tab = self.click_tab_by_index(index)
        self.get_element("tab-x-icon", parent_element=tab).click()
        return self

    def open_single_page_in_new_tab(self, page: BasePage, num_tabs: int) -> BasePage:
        """
        Opens a new tab, switches the driver context to the new tab, and opens the given webpage
        Arguments:
            page: The page object to open in the new tab
            num_tabs: Expected total number of tabs after opening the new tab (used for waiting)
        """
        self.new_tab_by_button()
        self.wait_for_num_tabs(num_tabs)
        self.driver.switch_to.window(self.driver.window_handles[-1])
        page.open()
        return self

    def open_multiple_tabs_with_pages(self, pages: list) -> "TabBar":
        """
        Opens multiple new tabs and navigates to different pages in each tab.

        Argument:
            pages: List of page objects or URLs to open in separate tabs
        """
        for page in pages:
            self.new_tab_by_button()
            self.wait_for_num_tabs(len(self.driver.window_handles))
            self.driver.switch_to.window(self.driver.window_handles[-1])

            if isinstance(page, str):
                self.driver.get(page)
            else:
                page.open()
        return self

    @BasePage.context_chrome
    def verify_tab_focus_cycle(self, num_tabs: int):
        """Go through all the tabs and ensure the focus changes correctly."""
        for i in range(1, num_tabs + 2):
            target_tab = self.get_tab(i)
            self.click_on(target_tab)
            self.custom_wait(timeout=3).until(
                lambda d: target_tab.get_attribute("visuallyselected") == ""
            )

    @BasePage.context_chrome
    def select_multiple_tabs_by_indices(
        self, indices: list[int], sys_platform: str
    ) -> list[WebElement]:
        """
        Selects multiple tabs based on their indices and returns list of tabs.

        Preconditions:
            - len(indices) > 1
            - max(indices) < number of open tabs
            - min(indices) >= 1
        Notes:
            - Opens (clicks) the tab at the first index in indices
            - the first tab in the window is denoted by index 1 (1-based indexing)
        """

        start_tab = self.get_tab(indices[0])
        selected_tabs = [start_tab]
        start_tab.click()

        actions = self.actions
        if sys_platform == "Darwin":
            actions.key_down(Keys.COMMAND).perform()
        else:
            actions.key_down(Keys.CONTROL).perform()

        for i in range(1, len(indices)):
            tab = self.get_tab(indices[i])
            actions.click(tab).perform()
            selected_tabs.append(tab)

        if sys_platform == "Darwin":
            actions.key_up(Keys.COMMAND).perform()
        else:
            actions.key_up(Keys.CONTROL).perform()

        return selected_tabs

    @BasePage.context_chrome
    def reopen_tabs_with_shortcut(self, sys_platform: str, count: int) -> None:
        """Reopen closed tabs using keyboard shortcut Ctrl/Cmd + Shift + T."""

        # Press modifier keys
        if sys_platform == "Darwin":
            self.actions.key_down(Keys.COMMAND).key_down(Keys.SHIFT).perform()
        else:
            self.actions.key_down(Keys.CONTROL).key_down(Keys.SHIFT).perform()

        # Press 'T' multiple times to reopen tabs
        for _ in range(count):
            self.actions.send_keys("t").perform()

        # Release modifier keys
        if sys_platform == "Darwin":
            self.actions.key_up(Keys.SHIFT).key_up(Keys.COMMAND).perform()
        else:
            self.actions.key_up(Keys.SHIFT).key_up(Keys.CONTROL).perform()

    @BasePage.context_chrome
    def reload_tab(self, nav, mod_key=None, extra_key=None):
        """
        Reloads the current tab using a keyboard shortcut inside Chrome context.

        Args:
            nav: Navigation object to click before sending keys.
            mod_key: Modifier key (e.g., Keys.CONTROL, Keys.COMMAND) for Ctrl/Cmd+R.
            extra_key: Extra key to press (e.g., 'r' for Ctrl/Cmd+R, or Keys.F5 for F5).
        """
        nav.click_on("navigation-background-component")

        # Determine which key combo to use
        if mod_key and extra_key:
            self.perform_key_combo(mod_key, extra_key)
        elif extra_key:
            self.perform_key_combo(extra_key)
        else:
            raise ValueError("You must provide extra_key to perform reload.")
