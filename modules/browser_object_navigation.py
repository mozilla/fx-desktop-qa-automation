import logging

from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains, Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

from modules.browser_object_context_menu import ContextMenu
from modules.browser_object_panel_ui import PanelUi
from modules.classes.bookmark import Bookmark
from modules.page_base import BasePage
from modules.util import BrowserActions


class Navigation(BasePage):
    """Page Object Model for nav buttons, AwesomeBar and toolbar"""

    URL_TEMPLATE = "about:blank"
    BROWSER_MODES = {
        "Bookmarks": "*",
        "Tabs": "%",
        "History": "^",
        "Actions": ">",
    }
    VALID_SEARCH_MODES = {
        "Google",
        "eBay",
        "Amazon.com",
        "Bing",
        "DuckDuckGo",
        "Wikipedia (en)",
    }

    def __init__(self, driver: Firefox, **kwargs):
        super().__init__(driver, **kwargs)
        self.search_bar = None
        self.awesome_bar = None
        self.change_search_settings_button = None
        self.bookmarks_toolbar = "bookmarks-toolbar"
        self.context_menu = ContextMenu(self.driver)
        self.panel_ui = PanelUi(self.driver)

    @BasePage.context_content
    def expect_in_content(self, condition) -> BasePage:
        """Like BasePage.expect, but guarantee we're looking at CONTEXT_CONTENT"""
        self.wait.until(condition)
        return self

    @BasePage.context_chrome
    def set_awesome_bar(self) -> BasePage:
        """Set the awesome_bar attribute of the Navigation object"""
        self.awesome_bar = self.get_element("awesome-bar")
        return self

    @BasePage.context_chrome
    def get_awesome_bar(self) -> WebElement:
        """Get the Awesome Bar. Prefer this over get_element."""
        self.set_awesome_bar()
        return self.awesome_bar

    @BasePage.context_chrome
    def get_awesome_bar_text(self):
        """
        Get the text directly from the awesome bar.
        This is different from 'driver.current_url' which pulls from href
        """
        awesome_bar = self.get_element("awesome-bar").get_attribute("value")
        return awesome_bar

    @BasePage.context_chrome
    def clear_awesome_bar(self) -> BasePage:
        """Clear the Awesome Bar. Prefer this over get_element("awesome-bar").clear()"""
        self.set_awesome_bar()
        self.awesome_bar.clear()
        return self

    @BasePage.context_chrome
    def type_in_awesome_bar(self, term: str) -> BasePage:
        """Enter text into the Awesome Bar. You probably want self.search()"""
        self.set_awesome_bar()
        self.awesome_bar.click()
        self.awesome_bar.send_keys(term)
        return self

    def set_search_mode_via_awesome_bar(self, mode: str) -> BasePage:
        """
        Given a `mode`, set the Awesome Bar search mode. Returns self.

        Parameter
        ---------
        mode: str
            The name of the search mode, or the keystroke shortcut (e.g. ^ for History)
        """
        if mode in self.BROWSER_MODES:
            abbr = self.BROWSER_MODES[mode]
        else:
            abbr = mode.lower()[:2]
        self.type_in_awesome_bar(abbr)
        self.wait.until(
            EC.visibility_of_element_located(
                self.get_selector("tab-to-search-text-span")
            )
        )
        self.awesome_bar.send_keys(Keys.TAB)
        self.wait.until(
            EC.text_to_be_present_in_element(
                self.get_selector("search-mode-span"), mode
            )
        )
        return self

    @BasePage.context_chrome
    def click_firefox_suggest(self) -> None:
        """Click the Firefox suggested result."""
        self.get_element("firefox-suggest").click()

    @BasePage.context_chrome
    def search(self, term: str, mode=None) -> BasePage:
        """
        Search using the Awesome Bar, optionally setting the search mode first. Returns self.

        Attributes
        ----------

        term : str
            The search term

        mode : str | None
            If set, the name or keystroke shortcut of the search mode
        """
        if mode:
            self.set_search_mode_via_awesome_bar(mode).type_in_awesome_bar(
                term + Keys.ENTER
            )
        else:
            self.type_in_awesome_bar(term + Keys.ENTER)
        return self

    @BasePage.context_chrome
    def set_search_bar(self) -> BasePage:
        """Set the search_bar attribute of the Navigation object"""
        self.search_bar = self.find_element(By.CLASS_NAME, "searchbar-textbox")
        return self

    @BasePage.context_chrome
    def search_bar_search(self, term: str) -> BasePage:
        """
        Search using the *Old* Search Bar. Returns self.

        Attributes
        ----------

        term : str
            The search term
        """
        self.search_bar = self.find_element(By.CLASS_NAME, "searchbar-textbox")
        self.search_bar.click()
        self.search_bar.send_keys(term + Keys.ENTER)
        return self

    @BasePage.context_chrome
    def type_in_search_bar(self, term: str) -> BasePage:
        """
        Type in the *Old* Search Bar. Returns self.

        Attributes
        ----------

        term : str
            The search term
        """
        self.search_bar = self.find_element(By.CLASS_NAME, "searchbar-textbox")
        self.search_bar.click()
        self.search_bar.send_keys(term)
        return self

    def open_awesome_bar_settings(self):
        """Open search settings from the awesome bar"""
        self.click_on("search-settings")
        return self

    @BasePage.context_chrome
    def click_on_change_search_settings_button(self) -> BasePage:
        self.search_bar = self.find_element(By.CLASS_NAME, "searchbar-textbox")
        self.search_bar.click()
        self.change_search_settings_button = self.find_element(
            By.ID, "searchbar-anon-search-settings"
        )
        self.change_search_settings_button.click()
        return self

    @BasePage.context_chrome
    def click_in_awesome_bar(self) -> BasePage:
        self.set_awesome_bar()
        self.awesome_bar.click()
        return self

    @BasePage.context_chrome
    def click_search_mode_switcher(self) -> BasePage:
        """
        click search mode switcher
        """
        self.search_mode_switcher = self.get_element("searchmode-switcher")
        self.search_mode_switcher.click()
        return self

    @BasePage.context_chrome
    def set_search_mode(self, search_mode: str) -> BasePage:
        """
        set new search location if search_mode in VALID_SEARCH_MODES

        Parameter:
            search_mode (str): search mode to be selected

        Raises:
            StopIteration: if a valid search mode is not found in the list of valid elements.
        """
        # check if search_mode is valid, otherwise raise error.
        if search_mode not in self.VALID_SEARCH_MODES:
            raise ValueError("search location is not valid.")
        # switch to chrome context
        # get list of all valid search modes and filter by label
        self.get_element("search-mode-switcher-option", labels=[search_mode]).click()
        return self

    @BasePage.context_chrome
    def context_click_in_awesome_bar(self) -> BasePage:
        self.set_awesome_bar()
        actions = ActionChains(self.driver)
        actions.context_click(self.awesome_bar).perform()
        return self

    @BasePage.context_chrome
    def get_download_button(self) -> WebElement:
        """
        Gets the download button WebElement
        """
        downloads_button = self.get_element("downloads-button")
        return downloads_button

    def click_download_button(self) -> BasePage:
        self.get_download_button().click()
        return self

    @BasePage.context_chrome
    def wait_for_download_animation_finish(
        self, downloads_button: WebElement
    ) -> BasePage:
        """
        Waits for the download button to finish playing the animation for downloading to local computer
        """
        try:
            self.wait.until(
                lambda _: downloads_button.get_attribute("notification") == "finish"
            )
        except TimeoutException:
            logging.warning("Animation did not finish or did not play.")
        return self

    @BasePage.context_chrome
    def open_tracker_panel(self) -> BasePage:
        """
        Clicks the shield icon and opens the panel associated with it
        """
        self.get_element("shield-icon").click()
        return self

    def wait_for_item_to_download(self, filename: str) -> BasePage:
        """
        Check the downloads tool in the toolbar to wait for a given file to download
        """
        original_timeout = self.driver.timeouts.implicit_wait
        try:
            # Whatever our timeout, we want to lengthen it because downloads
            self.driver.implicitly_wait(original_timeout * 2)
            self.element_visible("downloads-item-by-file", labels=[filename])
            self.expect_not(
                EC.element_attribute_to_include(
                    self.get_selector("downloads-button"), "animate"
                )
            )
            with self.driver.context(self.context_id):
                self.driver.execute_script(
                    "arguments[0].setAttribute('hidden', true)",
                    self.get_element("downloads-button"),
                )
        finally:
            self.driver.implicitly_wait(original_timeout)
        return self

    @BasePage.context_chrome
    def refresh_page(self) -> BasePage:
        """
        Refreshes the current page by clicking the refresh button in the browser.
        """

        self.get_element("refresh-button").click()
        self.wait_for_page_to_load()
        return self

    def handle_geolocation_prompt(self, button_type="primary"):
        """
        Handles geolocation prompt by clicking either the 'Allow' or 'Block' button based on the button_type provided
        """
        button_selector = f"popup-notification-{button_type}-button"
        self.element_clickable(button_selector)
        self.click_on(button_selector)

    def open_searchmode_switcher_settings(self):
        """Open search settings from searchmode switcher in awesome bar"""
        self.click_on("searchmode-switcher")
        self.click_on("searchmode-switcher-settings")
        return self

    @BasePage.context_chrome
    def select_element_in_nav(self, element: str) -> BasePage:
        self.get_element(element).click()
        return self

    @BasePage.context_chrome
    def get_legacy_search_engine_label(self) -> str:
        """Return the displayed engine name from the legacy search bar."""
        return self.driver.find_element(
            By.CSS_SELECTOR, ".searchbar-engine-name"
        ).get_attribute("value")

    # Bookmark

    @BasePage.context_chrome
    def add_bookmark_via_star_icon(self) -> BasePage:
        """
        Bookmark a site via star button and click save on the bookmark panel
        """
        self.click_on("star-button")
        self.panel_ui.click_on("save-bookmark-button")
        return self

    @BasePage.context_chrome
    def verify_star_button_is_blue(self) -> BasePage:
        """
        Verifies that the star button is blue (indicating a bookmarked page)
        """
        self.element_visible("blue-star-button")
        return self

    @BasePage.context_chrome
    def bookmark_page_in_other_bookmarks(self) -> BasePage:
        """
        Bookmark the current page in the Other Bookmarks folder via the star icon in the address bar.
        """
        self.click_on("star-button")
        self.panel_ui.click_on("bookmarks-type-dropdown")
        self.panel_ui.click_on("bookmarks-type-dropdown-other")
        self.panel_ui.click_on("save-bookmark-button")
        return self

    @BasePage.context_chrome
    def add_bookmark_via_toolbar_other_bookmark_context_menu(
        self, bookmark_data: Bookmark, ba: BrowserActions
    ) -> BasePage:
        """
        Add a bookmark via the toolbar's Other Bookmarks context menu.
        Arguments
        ----------
        bookmark_data : A Bookmark object containing the bookmark details to be added (name, url, tags, keyword)
        ba : BrowserActions utility
        """
        iframe = self.get_element("bookmark-iframe")
        ba.switch_to_iframe_context(iframe)
        # fill name
        self.actions.send_keys(bookmark_data.name).perform()
        self.actions.send_keys(Keys.TAB).perform()
        # fill url
        self.actions.send_keys(bookmark_data.url + Keys.TAB).perform()
        # fill tags
        self.actions.send_keys(bookmark_data.tags).perform()
        self.actions.send_keys(Keys.TAB).perform()
        self.actions.send_keys(Keys.TAB).perform()
        # fill keywords
        self.actions.send_keys(bookmark_data.keyword).perform()
        # save the bookmark
        self.actions.send_keys(Keys.ENTER).perform()
        return self

    @BasePage.context_chrome
    def toggle_bookmarks_toolbar_with_key_combo(self) -> BasePage:
        """Use Cmd/Ctrl + B to open the Print Preview, wait for load"""

        if self.sys_platform() == "Darwin":
            mod_key = Keys.COMMAND
        else:
            mod_key = Keys.CONTROL
        self.perform_key_combo(mod_key, Keys.SHIFT, "b")
        return self

    @BasePage.context_chrome
    def confirm_bookmark_exists(self, match_string: str) -> BasePage:
        """
        For a given string, return self if it exists in the label of a bookmark, else assert False.
        """

        bookmarks = self.get_elements("bookmark-in-bar")
        logging.info(f"Found {len(bookmarks)} bookmarks.")
        for el in bookmarks:
            logging.info(el.get_attribute("label"))

        matches_short_string = any(
            [match_string in el.get_attribute("label") for el in bookmarks]
        )
        matches_long_string = any(
            [el.get_attribute("label") in match_string for el in bookmarks]
        )
        assert matches_short_string or matches_long_string
        return self

    @BasePage.context_chrome
    def open_add_bookmark_via_toolbar_other_bookmarks_context_menu(self) -> BasePage:
        """
        Open the context menu for Other Bookmarks in the toolbar and select Add Bookmark option.
        """
        self.click_on("other-bookmarks-toolbar")
        self.context_click("other-bookmarks-popup")
        self.context_menu.click_on("context-menu-add-bookmark")
        self.context_menu.hide_popup_by_child_node("context-menu-add-bookmark")
        self.hide_popup("OtherBookmarksPopup")
        return self

    @BasePage.context_chrome
    def delete_bookmark_from_other_bookmarks_via_context_menu(
        self, bookmark_name: str
    ) -> BasePage:
        """
        Deletes a bookmark from Other Bookmarks via context menu.
        Argument:
        ----------
        bookmark_name: The display name of the bookmark to delete
        """
        self.click_on("other-bookmarks-toolbar")
        self.panel_ui.context_click("other-bookmarks-by-title", labels=[bookmark_name])
        self.context_menu.click_and_hide_menu("context-menu-delete-page")
        return self

    @BasePage.context_chrome
    def delete_bookmark_from_bookmarks_toolbar(self, bookmark_name: str) -> BasePage:
        """
        Delete bookmark from bookmarks toolbar via context menu
        Argument:
        ----------
        bookmark_name: The display name of the bookmark to delete
        """
        self.panel_ui.context_click("bookmark-by-title", labels=[bookmark_name])
        self.context_menu.click_and_hide_menu("context-menu-delete-page")
        return self

    @BasePage.context_chrome
    def verify_bookmark_exists_in_toolbar_other_bookmarks_folder(
        self, bookmark_name: str
    ) -> BasePage:
        """
        Verify bookmark exists in Other Bookmarks folder from toolbar
        Arguments
        ----------
        bookmark_name : The exact name/title of the bookmark to search for in the Other Bookmarks folder.
        """
        self.click_on("other-bookmarks-toolbar")  # Navigation selector
        self.panel_ui.element_visible(
            "other-bookmarks-by-title", labels=[bookmark_name]
        )
        return self

    @BasePage.context_chrome
    def verify_bookmark_exists_in_bookmarks_toolbar(
        self, bookmark_name: str
    ) -> BasePage:
        """
        Verify bookmark exists in the bookmarks toolbar
        """
        self.panel_ui.element_visible("bookmark-by-title", labels=[bookmark_name])
        return self

    @BasePage.context_chrome
    def verify_bookmark_does_not_exist_in_toolbar_other_bookmarks_folder(
        self, bookmark_name: str
    ) -> BasePage:
        """
        Verify bookmark does not exist in Other Bookmarks folder from toolbar
        Arguments
        ----------
        bookmark_name : The exact name/title of the bookmark to search for in the Other Bookmarks folder.
        """
        self.click_on("other-bookmarks-toolbar")
        self.panel_ui.element_not_visible(
            "other-bookmarks-by-title", labels=[bookmark_name]
        )
        return self

    @BasePage.context_chrome
    def verify_bookmark_does_not_exist_in_bookmarks_toolbar(
        self, bookmark_name: str
    ) -> BasePage:
        """Verify bookmark does not exist in the bookmarks toolbar"""
        self.panel_ui.element_not_visible("bookmark-by-title", labels=[bookmark_name])
        return self

    @BasePage.context_chrome
    def edit_bookmark_via_star_button(self, new_name: str, location: str) -> BasePage:
        """
        Edit bookmark details by opening the edit bookmark panel via the star button
        Arguments
        ----------
        new_name : str
            The new name/title to assign to the bookmark
        location : str
            The folder location where the bookmark should be saved
        """
        self.click_on("star-button")
        self.panel_ui.get_element("edit-bookmark-panel").send_keys(new_name)
        if location == "Other Bookmarks":
            self.panel_ui.click_on("bookmark-location")
            self.panel_ui.click_on("other-bookmarks")
        elif location == "Bookmarks Toolbar":
            self.panel_ui.click_on("bookmark-location")
            self.panel_ui.click_on("bookmarks-toolbar")
        self.panel_ui.click_on("save-bookmark-button")
        return self

    @BasePage.context_chrome
    def toggle_show_editor_when_saving(self) -> BasePage:
        """
        Toggle the show editor checkbox
        """
        self.click_on("star-button")
        self.panel_ui.click_on("show-editor-when-saving-checkbox")
        self.panel_ui.click_on("save-bookmark-button")
        return self

    @BasePage.context_chrome
    def verify_edit_bookmark_panel_not_visible_after_navigation(self) -> BasePage:
        """
        Navigate to new URL and verify that edit bookmark panel is not visible when clicking star
        Uses the exact same pattern as the working test
        """
        self.click_on("star-button")
        self.panel_ui.element_not_visible("show-editor-when-saving-checkbox")
        return self

    def open_bookmark_from_toolbar(self, bookmark_title: str) -> BasePage:
        """
        Right-clicks bookmark and opens it in a new private window via context menu
        Arguments:
            bookmark_title: The title of the bookmark to open
        """
        self.panel_ui.element_clickable("bookmark-by-title", labels=[bookmark_title])
        self.panel_ui.context_click("bookmark-by-title", labels=[bookmark_title])
        return self

    @BasePage.context_chrome
    def open_bookmark_in_new_window_via_context_menu(
        self, bookmark_title: str
    ) -> BasePage:
        """
        Right-click bookmark and opens it in a new window via context menu
        Arguments:
            bookmark_title: The title of the bookmark to open
        """
        self.panel_ui.element_clickable("bookmark-by-title", labels=[bookmark_title])
        self.panel_ui.context_click("bookmark-by-title", labels=[bookmark_title])
        self.context_menu.click_on("context-menu-toolbar-open-in-new-window")
        return self

    @BasePage.context_chrome
    def open_bookmark_in_new_private_window_via_context_menu(
        self, bookmark_title: str
    ) -> BasePage:
        """
        Right-clicks bookmark and opens it in a new private window via context menu
        Arguments:
            bookmark_title: The title of the bookmark to open
        """
        self.panel_ui.element_clickable("bookmark-by-title", labels=[bookmark_title])
        self.panel_ui.context_click("bookmark-by-title", labels=[bookmark_title])
        self.context_menu.click_on("context-menu-toolbar-open-in-new-private-window")
        return self

    @BasePage.context_chrome
    def open_all_bookmarks_via_context_menu(self) -> BasePage:
        """
        Right-clicks on bookmarks toolbar and opens all bookmarks via context menu
        """
        self.context_click("bookmarks-toolbar")
        self.context_menu.click_on("context-menu-toolbar-open-all-bookmarks")
        return self

    @BasePage.context_chrome
    def expect_bookmarks_toolbar_visibility(self, expected: bool) -> None:
        """
        Assert the visibility state of the Bookmarks Toolbar.

        Arguments:
        ----------
        expected (bool):
            If True, asserts that the toolbar is visible (collapsed="false").
            If False, asserts that the toolbar is hidden (collapsed="true")
        """

        expected_value = "false" if expected else "true"
        self.expect_element_attribute_contains(
            self.bookmarks_toolbar, "collapsed", expected_value
        )
