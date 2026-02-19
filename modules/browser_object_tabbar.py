import logging
from time import sleep
from typing import Union

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

from modules.browser_object import ContextMenu
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

    @BasePage.context_chrome
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
    def wait_and_switch_to_new_tab(self, num_tabs: int = 0):
        """
        wait till a new tab is opened and switch to it.
        """
        if num_tabs:
            self.wait_for_num_tabs(num_tabs)
        self.switch_to_new_tab()

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
        """Given a tab index (int), click the corresponding tab and wait for it to be selected"""
        tab = self.get_element("tab-by-index", labels=[str(index)])
        tab.click()
        self.expect(lambda _: tab.get_attribute("selected") == "true")
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

    @BasePage.context_chrome
    def close_last_n_tabs(self, total_tabs: int, count: int) -> "TabBar":
        """
        Close the last N tabs in the current window, starting from the rightmost tab.
        Arguments:
            total_tabs: Total number of tabs currently open in the window
            count: Number of tabs to close from the end
        """
        for offset in range(count):
            tab_index = total_tabs - offset
            tab = self.get_tab(tab_index)
            if tab:
                self.close_tab(tab)
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

    def open_urls_in_tabs(self, urls: list, open_first_in_current_tab: bool = False):
        """
        Opens URLs in tabs. By default, opens a new tab for each URL.
        Arguments:
            urls: List of URLs to open in tabs
            open_first_in_current_tab: If True, opens first URL in current tab instead of new tab
        """
        for i, url in enumerate(urls):
            if i == 0 and open_first_in_current_tab:
                with self.driver.context(self.driver.CONTEXT_CONTENT):
                    self.driver.get(url)
            else:
                self.new_tab_by_button()
                self.wait_for_num_tabs(len(self.driver.window_handles))
                self.driver.switch_to.window(self.driver.window_handles[-1])
                self.driver.get(url)
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

        # Press "T" multiple times to reopen tabs
        for _ in range(count):
            self.actions.send_keys("t").perform()
            # Pause a moment to let each tab to reopen
            sleep(0.2)

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

    @BasePage.context_chrome
    def create_tab_group(
        self, num_tabs: int, group_name: str, tab_context_menu: ContextMenu
    ) -> BasePage:
        """Create a new tab group"""

        # Open few tabs
        for i in range(num_tabs):
            self.new_tab_by_button()

        # Add the first tab into a New Group
        first_tab = self.get_tab(1)
        self.context_click(first_tab)
        tab_context_menu.click_and_hide_menu("context-move-tab-to-new-group")

        # Wait for tab group menu to open
        self.element_visible("tabgroup-input")

        # Enter a group Name and create group
        self.fill("tabgroup-input", group_name, clear_first=False)

        # Make sure the group is created
        self.element_visible("tabgroup-label")

        # Add the second tab into existing Group
        second_tab = self.get_tab(2)
        self.context_click(second_tab)
        tab_context_menu.click_on("context-move-tab-to-group")
        self.click_and_hide_menu("tabgroup-menuitem")
        self.hide_popup("tabContextMenu")

        return self

    @BasePage.context_chrome
    def get_tab_group_color(self) -> str:
        """Return the color attribute of the first tab group"""
        return self.get_element("tabgroup").get_attribute("color")

    @BasePage.context_chrome
    def get_tab_group_label(self) -> str:
        """Return the text of the tab group label"""
        return self.get_element("tabgroup-label").text

    @BasePage.context_chrome
    def edit_tab_group(
        self, new_name: str = None, new_color: str = None, add_new_tab: bool = False
    ) -> "TabBar":
        """
        Edit an existing tab group's name, color, and/or add a new tab.
        Arguments:
            new_name: New name for the tab group (optional)
            new_color: New color for the tab group (optional) - e.g. "purple", "blue", "red"
            add_new_tab: Whether to add a new tab to the group (default False)
        """
        # Open the editor panel
        self.context_click("tabgroup-label")
        self.element_visible("tabgroup-menu")

        # Edit the name if provided
        if new_name:
            self.triple_click("tabgroup-name-input")
            self.fill(
                "tabgroup-name-input", new_name, clear_first=False, press_enter=False
            )

        # Change the color if provided (use JS click as the label element is not directly clickable)
        if new_color:
            color_swatch = self.get_element("tabgroup-color-swatch", labels=[new_color])
            self.driver.execute_script("arguments[0].click();", color_swatch)

        # Add a new tab if requested
        if add_new_tab:
            self.click_on("tabgroup-add-new-tab")

        return self

    @BasePage.context_chrome
    def save_and_close_tab_group(self) -> BasePage:
        """
        Right-click the Tab Group label and select Save and Close Group.
        This closes all tabs in the group and removes the group label.
        """
        self.context_click("tabgroup-label")
        self.element_visible("tabgroup-menu")
        save_btn = self.get_element("tabgroup-save-and-close-group")
        self.click_on(save_btn)
        return self

    @BasePage.context_chrome
    def expect_play_tab_button(self, visible: bool = True) -> BasePage:
        """
        Wait for the 'Play Tab' button to be visible/hidden on the tab.
        Argument:
            visible: True to expect button visible, False to expect hidden
        """
        if visible:
            self.element_visible("play-tab-button", labels=["true"])
        else:
            assert self.get_elements("play-tab-button", labels=["true"]) == []
        return self

    @BasePage.context_chrome
    def get_active_tab_group_label(self) -> str:
        """Return the group label of the currently active tab"""
        # Get all tabs
        tabs = self.get_elements("all-tabs")

        # Find selected tab index
        selected_index = next(
            i for i, t in enumerate(tabs) if t.get_attribute("selected") == "true"
        )

        # Get all group labels in order
        group_labels = [g.text for g in self.get_elements("tabgroup-label")]

        # Map tab index to group label
        # This assumes tabs are added to groups in order, matching your test setup
        if selected_index < 2:
            return group_labels[0]
        else:  # second group
            return group_labels[1]

    def open_and_switch_to_new_tab(self) -> BasePage:
        """
        Opens a new tab then switches to it.
        """
        cur_tabs = len(self.driver.window_handles)
        self.new_tab_by_button()
        self.wait_for_num_tabs(cur_tabs + 1)
        self.switch_to_new_tab()
        return self

    def create_websites_tab_group(
        self,
        context_menu: ContextMenu,
        group_name: str,
        first_tab_index: int,
        additional_tab_indexes: list[int],
    ) -> None:
        """Create a tab group and add tabs to it"""

        # Create the group with the first tab
        first_tab = self.get_tab(first_tab_index)
        self.context_click(first_tab)
        context_menu.click_and_hide_menu("context-move-tab-to-new-group")

        self.element_visible("tabgroup-input")
        self.fill("tabgroup-input", group_name, clear_first=False)
        self.element_visible("tabgroup-label")

        # Add remaining tabs to the group
        for index in additional_tab_indexes:
            tab = self.get_tab(index)
            self.context_click(tab)
            context_menu.click_on("context-move-tab-to-group")
            self.click_and_hide_menu("tabgroup-menuitem")
            self.hide_popup("tabContextMenu")

    @BasePage.context_chrome
    def add_tab_to_existing_group(self, tab_index: int, context_menu: ContextMenu):
        """
        Add a tab to an existing tab group.
        Arguments:
            tab_index: The index of the tab to add to the group
            context_menu: ContextMenu instance
        """
        tab = self.get_tab(tab_index)
        self.context_click(tab)
        context_menu.click_on("context-move-tab-to-group")
        self.click_and_hide_menu("tabgroup-menuitem")
        self.hide_popup("tabContextMenu")
        return self

    @BasePage.context_chrome
    def remove_tab_from_group(self, tab_index: int, context_menu: ContextMenu):
        """
        Remove a tab from its group via context menu.
        Arguments:
            tab_index: The index of the tab to remove from the group
            context_menu: ContextMenu instance
        """
        tab = self.get_tab(tab_index)
        self.context_click(tab)
        context_menu.click_and_hide_menu("context-remove-tab-from-group")
        self.hide_popup("tabContextMenu")
        return self

    @BasePage.context_chrome
    def get_tab_position(self, tab_index: int):
        """
        Get the visual position of a tab in the tab strip. Returns the x-coordinate of the tab.
        Argument:
            tab_index: The index of the tab to get the position of
        """
        tab = self.get_tab(tab_index)
        return tab.location["x"]

    @BasePage.context_chrome
    def verify_removed_tab_displayed_after_group(self, tab_index: int):
        """
        Verify that a tab is positioned after the tab group in the tab strip.
        Argument:
            tab_index: The index of the tab to verify
        """
        tab_position = self.get_tab_position(tab_index)
        group = self.get_element("tabgroup")
        group_end_position = group.location["x"] + group.size["width"]
        assert tab_position >= group_end_position, (
            f"Expected tab to be after the group. "
            f"Tab position: {tab_position}, Group end: {group_end_position}"
        )
        return self

    @BasePage.context_chrome
    def verify_hover_preview(self, total_tabs: int, expect_thumbnail: bool = True):
        """
        Hover over each tab and verify the hover preview panel is displayed.
        Arguments:
            total_tabs: Total number of tabs to hover over
            expect_thumbnail: If True, verify panel with Name and URL.
                              If False, also assert thumbnail container is not visible.
        """
        for i in range(1, total_tabs + 1):
            tab = self.get_tab(i)
            self.hover(tab)
            self.element_visible("tab-preview-panel")
            self.element_visible("tab-preview-title")
            self.element_visible("tab-preview-uri")

            if not expect_thumbnail:
                self.element_not_visible("tab-preview-thumbnail-container")
        return self

    def get_all_window_urls(self) -> set[str]:
        """Get URLs from all open windows/tabs.
        Iterates through all window handles and collects current URLs
        """
        urls = set()
        with self.driver.context(self.driver.CONTEXT_CONTENT):
            for handle in self.driver.window_handles:
                self.driver.switch_to.window(handle)
                urls.add(self.driver.current_url)
        return urls
