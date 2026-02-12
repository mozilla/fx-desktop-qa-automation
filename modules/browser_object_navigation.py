import logging
import re
import time
from typing import Callable, Literal
from urllib.parse import urlparse

from selenium.common.exceptions import (
    InvalidSessionIdException,
    NoSuchWindowException,
    StaleElementReferenceException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver import ActionChains, Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

from modules.browser_object_context_menu import ContextMenu
from modules.browser_object_panel_ui import PanelUi
from modules.classes.bookmark import Bookmark
from modules.page_base import BasePage
from modules.page_object_customize_firefox import CustomizeFirefox
from modules.util import BrowserActions


class Navigation(BasePage):
    """Page Object Model for nav buttons, AwesomeBar and toolbar"""

    URL_TEMPLATE = "about:blank"

    # XPath selectors for Firefox's PanelMultiView widget system. The Library menu is a stack of nested subviews.
    # When you navigate deeper, Firefox keeps the previous views in the DOM and just marks them as offscreen. These
    # XPaths help us target the currently active/visible view. They live here (not in the JSON selectors) because
    # they're "state" checks for panel transitions, not a single element we interact with.
    XPATH_LIBRARY_RECENTLY_CLOSED_TABS_VIEW_VISIBLE = (
        "//*[@id='appMenu-library-recentlyClosedTabs' and @visible='true' "
        "and not(ancestor::*[contains(concat(' ', normalize-space(@class), ' '), ' offscreen ')])]"
    )
    XPATH_PANEL_OPEN = "//*[@panelopen='true']"
    XPATH_RECENTLY_CLOSED_TABS_NOT_OFFSCREEN = (
        "//*[@id='appMenuRecentlyClosedTabs' and not(ancestor::*[contains(concat(' ', normalize-space("
        "@class), ' '), ' offscreen ')])]"
    )
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
        "Firefox Add-ons",
    }
    _TARGET_URI_RE = re.compile(r'targetURI="([^"]+)"', re.IGNORECASE)

    def __init__(self, driver: Firefox, **kwargs):
        super().__init__(driver, **kwargs)
        self.search_bar = None
        self.awesome_bar = None
        self.change_search_settings_button = None
        self.bookmarks_toolbar = "bookmarks-toolbar"
        self.context_menu = ContextMenu(self.driver)
        self.panel_ui = PanelUi(self.driver)
        self.customize = CustomizeFirefox(self.driver)

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
    def type_in_awesome_bar(self, term: str, reset=True) -> BasePage:
        """
        Type text into the Awesome Bar.

        reset=True (default): refocuses and clicks the Awesome Bar before typing,
        which moves the cursor to the end.

        reset=False: keeps the current cursor position (useful when tests manually
        move the caret with arrow keys).
        """
        if reset:
            self.set_awesome_bar()
            self.awesome_bar.click()

        self.awesome_bar.send_keys(term)
        return self

    @BasePage.context_chrome
    def verify_result_term(self, url):
        """
        Verify the result url and action term after typing in the Awesome Bar.
        """
        url_element = self.get_element("search-result-url")
        action_element = self.get_element("search-result-action-term")
        self.expect(lambda _: (url_element.text, action_element.text) == (url, "Visit"))

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
    def click_switch_to_tab(self) -> None:
        """
        Clicks the 'Switch to Tab' suggestion in the URL bar results.
        Assumes the caller already typed into the awesome bar.

        This uses a minimal wait that returns the list of matches only
        when at least one element is found.
        """

        # Wait until at least one switch-to-tab result is present
        switch_items = self.wait.until(
            lambda d: self.get_elements("switch-to-tab") or None
        )

        # Click the first matching row
        switch_items[0].click()

    @BasePage.context_chrome
    def click_on_clipboard_suggestion(self) -> None:
        """
        Click the 'Visit from clipboard' suggestion in the URL bar.
        Requires:
          - browser.urlbar.clipboard.featureGate = true
          - Clipboard suggestion already visible
        """
        row = self.wait.until(lambda d: self.get_element("clipboard-suggestion"))
        row.click()

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

    @BasePage.context_chrome
    def click_download_button(self) -> BasePage:
        self.get_download_button().click()
        return self

    @BasePage.context_chrome
    def wait_for_download_animation_finish(self) -> BasePage:
        """Waits for the download button to finish playing the animation"""
        try:
            downloads_button = self.get_download_button()
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

    @BasePage.context_chrome
    def assert_blocked_trackers(self, *blocked_trackers) -> BasePage:
        """
        Given a list of blocked trackers, assert that they are present in the blocked list.
        """
        self.open_tracker_panel()
        if blocked_trackers:
            for tracker in blocked_trackers:
                self.element_visible(tracker)
        else:
            self.get_element("no-trackers-detected").is_displayed()

    @BasePage.context_chrome
    def verify_cross_site_trackers(self, cross_site_trackers, allowed_cookies):
        """
        Verify that the list of cross-site trackers is as expected.
        """
        for val in cross_site_trackers:
            self.expect(lambda _: val in allowed_cookies)

    def search_and_check_if_suggestions_are_present(
        self, text, search_mode: str = "awesome", min_suggestions=1
    ):
        """
        Search in the given address bar and check if suggestions are present.

        Args:
            text (str): Text to search for in the suggestions.
            search_mode(str): Search mode to use. Can be 'awesome' or 'search'. Defaults to 'awesome'.
            min_suggestions (int): Minimum number of suggestions to collect.
        """
        if search_mode == "awesome":
            self.clear_awesome_bar()
            self.type_in_awesome_bar(text)
            time.sleep(0.5)
            return self.awesome_bar_has_suggestions(min_suggestions)
        elif search_mode == "search":
            self.set_search_bar()
            self.type_in_search_bar(text)
            return self.search_bar_has_suggestions(min_suggestions)
        else:
            raise ValueError("search_mode must be either 'awesome' or 'search'")

    @BasePage.context_chrome
    def awesome_bar_has_suggestions(self, min_suggestions: int = 1) -> bool:
        """Check if the awesome bar has any suggestions."""
        self.wait_for_suggestions_present(min_suggestions)
        suggestion_container = self.get_element("results-dropdown")
        has_children = self.driver.execute_script(
            f"return arguments[0].children.length > {min_suggestions};",
            suggestion_container,
        )
        return has_children

    def verify_no_external_suggestions(
        self,
        text: str | None = None,
        search_mode: str = "awesome",
        max_rows: int = 3,
        type_delay: float = 0.3,
    ) -> bool:
        if search_mode == "awesome":
            if text is not None:
                self.clear_awesome_bar()
                self.type_in_awesome_bar(text)
                time.sleep(type_delay)  # allow dropdown to update

            suggestions = self.get_all_children("results-dropdown")
            return len(suggestions) <= max_rows

        elif search_mode == "search":
            if text is not None:
                self.set_search_bar()
                self.type_in_search_bar(text)
            return not self.search_bar_has_suggestions(min_suggestions=1)

        else:
            raise ValueError("search_mode must be either 'awesome' or 'search'")

    @BasePage.context_chrome
    def search_bar_has_suggestions(self, min_suggestions: int = 0) -> bool:
        """Check if the legacy search bar has suggestions. if a style has max-height: 0px, then no suggestions are present."""
        suggestion_container = self.get_element(
            "legacy-search-mode-suggestion-container"
        )
        if min_suggestions > 2:
            return (
                suggestion_container.find_element(By.XPATH, "./*[1]").tag_name
                == "richlistitem"
            )
        else:
            has_children = self.driver.execute_script(
                "return arguments[0].children.length > 0;", suggestion_container
            )
            return has_children

    def wait_for_suggestions_present(self, at_least: int = 1):
        """Wait until the suggestion list has at least one visible item."""
        self.set_chrome_context()
        self.expect(lambda _: len(self.get_elements("suggestion-titles")) >= at_least)
        return self

    def wait_for_suggestions_absent(self):
        """Wait for the suggestions list to disappear (for non-general engines)."""
        self.set_chrome_context()
        self.element_not_visible("suggestion-titles")
        return self

    @BasePage.context_chrome
    def open_usb_and_select_option(self, option_title: str):
        """Click the USB icon and select an option by its title."""
        self.get_element("searchmode-switcher").click()
        self.get_element("search-mode-switcher-option", labels=[option_title]).click()
        return self

    def assert_search_mode_chip_visible(self):
        """Ensure the search mode indicator (chip) is visible on the left."""
        self.set_chrome_context()
        self.get_element("search-mode-span")
        return self

    @BasePage.context_chrome
    def verify_search_mode_is_visible(self):
        """Ensure the search mode is visible in URLbar"""
        self.element_visible("search-mode-chicklet")
        return self

    @BasePage.context_chrome
    def verify_search_mode_is_not_visible(self):
        """Ensure the search mode is cleared from URLbar"""
        self.element_not_visible("search-mode-chicklet")
        return self

    @BasePage.context_chrome
    def verify_search_mode_label(self, engine_name: str):
        """Verify that the search mode chicklet displays the correct engine."""
        chicklet = self.get_element("search-mode-chicklet")
        chip_text = (
            chicklet.text or chicklet.get_attribute("aria-label") or ""
        ).lower()
        assert engine_name.lower() in chip_text, (
            f"Expected search mode engine '{engine_name}', got '{chip_text}'"
        )
        return self

    @BasePage.context_chrome
    def verify_plain_text_in_input_awesome_bar(self, expected_text: str):
        """Verify the awesomebar input contains the exact literal text."""
        input_el = self.get_element("awesome-bar")
        value = input_el.get_attribute("value")
        assert value == expected_text, (
            f"Expected input '{expected_text}', got '{value}'"
        )
        return self

    def click_first_suggestion_row(self):
        """
        Clicks the first visible suggestion row in the list, using robust scrolling and fallback.
        """
        from selenium.webdriver.common.action_chains import ActionChains
        from selenium.webdriver.common.by import By

        self.set_chrome_context()
        driver = self.driver

        try:
            # Prefer Firefox Suggest row if present
            row = self.get_element("firefox-suggest")
        except Exception:
            titles = self.get_elements("suggestion-titles")
            assert titles, "No visible suggestion items found."
            target = next((t for t in titles if t.is_displayed()), titles[0])
            try:
                row = target.find_element(
                    By.XPATH, "ancestor::*[contains(@class,'urlbarView-row')][1]"
                )
            except Exception:
                row = target

        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", row)
        try:
            ActionChains(driver).move_to_element(row).click().perform()
        except Exception:
            driver.execute_script("arguments[0].click();", row)

        return self

    @BasePage.context_chrome
    def click_file_download_warning_panel(self) -> BasePage:
        """exit file download warning panel if present"""
        self.element_clickable("file-download-warning-button")
        self.click_on("file-download-warning-button")
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
    def verify_download_name(self, expected_pattern: str) -> BasePage:
        """
        Verify download name matches expected pattern.
        Argument:
            expected_pattern: Regex pattern to match against download name
        """
        download_name = self.get_element("download-target-element")
        download_value = download_name.get_attribute("value")
        assert re.match(expected_pattern, download_value), (
            f"The download name is incorrect: {download_value}"
        )
        return self

    @BasePage.context_chrome
    def wait_for_download_completion(self) -> BasePage:
        """Wait until the most recent download reaches 100% progress."""

        def _download_complete(_):
            try:
                element = self.get_element("download-progress-element")
                return element.get_attribute("value") == "100"
            except StaleElementReferenceException:
                return False

        self.wait.until(_download_complete)
        return self

    @BasePage.context_chrome
    def refresh_page(self) -> BasePage:
        """
        Refreshes the current page by clicking the refresh button in the browser.
        """

        self.get_element("refresh-button").click()
        self.wait_for_page_to_load()
        return self

    @BasePage.context_chrome
    def hard_reload_with_key_combo(self) -> BasePage:
        """
        Use Cmd/Ctrl + Shift + R to hard reload the page and overide cache.
        """
        if self.sys_platform() == "Darwin":
            mod_key = Keys.COMMAND
        else:
            mod_key = Keys.CONTROL
        self.perform_key_combo(mod_key, Keys.SHIFT, "r")
        return self

    def handle_geolocation_prompt(
        self, button_type="primary", remember_this_decision=False
    ):
        """
        Handles geolocation prompt by clicking either the 'Allow' or 'Block' button based on the button_type provided
        """
        button_selector = f"popup-notification-{button_type}-button"
        self.element_clickable(button_selector)
        if remember_this_decision:
            self.click_on("checkbox-remember-this-decision")
        self.click_on(button_selector)

    def open_searchmode_switcher_settings(self):
        """Open search settings from searchmode switcher in awesome bar"""
        self.click_on("searchmode-switcher")
        self.click_on("searchmode-switcher-settings")
        self.switch_to_new_tab()
        return self

    @BasePage.context_chrome
    def select_element_in_nav(self, element: str) -> BasePage:
        self.get_element(element).click()
        return self

    @BasePage.context_chrome
    def open_forget_panel(self) -> BasePage:
        """Open the Forget Panel by clicking the Forget button in the toolbar."""
        self.get_element("forget-button").click()
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

        Arguments:
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
        """
        Use Cmd/Ctrl + B to open the Print Preview, wait for load
        """
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
        bookmark_name: The display name of the bookmark to delete
        """
        self.click_on("other-bookmarks-toolbar")
        self.panel_ui.context_click("other-bookmarks-by-title", labels=[bookmark_name])
        self.context_menu.click_and_hide_menu("context-menu-delete-page")
        return self

    @BasePage.context_chrome
    def delete_panel_menu_item_by_title(self, item_title: str) -> BasePage:
        """
        Delete a panel menu item (bookmark or history entry) via context menu.

        This method works for both bookmarks and history items in the panel menu (hamburger menu),
        as Firefox uses the same UI structure for both. The caller should ensure the appropriate
        panel menu is open (e.g., History menu or Bookmarks menu) before calling this method.

        Argument:
            item_title: The display name/title of the item to delete (works for both bookmarks and history entries)
        """
        self.panel_ui.context_click("panel-menu-item-by-title", labels=[item_title])
        self.context_menu.click_and_hide_menu("context-menu-delete-page")
        return self

    @BasePage.context_chrome
    def verify_bookmark_exists_in_toolbar_other_bookmarks_folder(
        self, bookmark_name: str
    ) -> BasePage:
        """
        Verify bookmark exists in Other Bookmarks folder from toolbar

        Argument:
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
        self.panel_ui.element_visible(
            "panel-menu-item-by-title", labels=[bookmark_name]
        )
        return self

    @BasePage.context_chrome
    def verify_bookmark_does_not_exist_in_toolbar_other_bookmarks_folder(
        self, bookmark_name: str
    ) -> BasePage:
        """
        Verify bookmark does not exist in Other Bookmarks folder from toolbar

        Argument:
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
        self.panel_ui.element_not_visible(
            "panel-menu-item-by-title", labels=[bookmark_name]
        )
        return self

    @BasePage.context_chrome
    def edit_bookmark_via_star_button(
        self, new_name: str, location: str, save_bookmark: True
    ) -> BasePage:
        """
        Edit bookmark details by opening the edit bookmark panel via the star button

        Arguments:
        new_name : The new name/title to assign to the bookmark
        location : The folder location where the bookmark should be saved
        action_complete:
        """
        self.click_on("star-button")
        # Wait a moment for the panel edit field to gain focus then delete the contents,
        # otherwise new_name text can be appended to the original name instead of replacing it
        time.sleep(0.5)
        self.panel_ui.get_element("edit-bookmark-panel").send_keys(
            Keys.DELETE + new_name
        )
        if location == "Other Bookmarks":
            self.panel_ui.click_on("bookmark-location")
            self.panel_ui.click_on("other-bookmarks")
        elif location == "Bookmarks Toolbar":
            self.panel_ui.click_on("bookmark-location")
            self.panel_ui.click_on("bookmarks-toolbar")
        if not save_bookmark:
            return self
        else:
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

    @BasePage.context_chrome
    def open_bookmark_from_toolbar(self, bookmark_title: str) -> BasePage:
        """
        Clicks a bookmark on the bookmark toolbar to open it in the current tab

        Argument:
            bookmark_title: The title of the bookmark to open
        """
        self.panel_ui.element_clickable(
            "panel-menu-item-by-title", labels=[bookmark_title]
        )
        self.panel_ui.click_on("panel-menu-item-by-title", labels=[bookmark_title])
        return self

    @BasePage.context_chrome
    def open_bookmark_in_new_tab_via_context_menu(
        self, bookmark_title: str
    ) -> BasePage:
        """
        Right-click bookmark and opens it in a new tab via context menu

        Argument:
            bookmark_title: The title of the bookmark to open
        """
        # Right-click the bookmark and open it in new tabe via context menu item
        self.panel_ui.element_clickable(
            "panel-menu-item-by-title", labels=[bookmark_title]
        )
        self.panel_ui.context_click("panel-menu-item-by-title", labels=[bookmark_title])
        self.context_menu.click_on("context-menu-toolbar-open-in-new-tab")

        return self

    @BasePage.context_chrome
    def open_bookmark_in_new_window_via_context_menu(
        self, bookmark_title: str
    ) -> BasePage:
        """
        Right-click bookmark and opens it in a new window via context menu

        Argument:
            bookmark_title: The title of the bookmark to open
        """
        self.panel_ui.element_clickable(
            "panel-menu-item-by-title", labels=[bookmark_title]
        )
        self.panel_ui.context_click("panel-menu-item-by-title", labels=[bookmark_title])
        self.context_menu.click_on("context-menu-toolbar-open-in-new-window")
        return self

    @BasePage.context_chrome
    def open_bookmark_in_new_private_window_via_context_menu(
        self, bookmark_title: str
    ) -> BasePage:
        """
        Right-clicks bookmark and opens it in a new private window via context menu

        Argument:
            bookmark_title: The title of the bookmark to open
        """
        self.panel_ui.element_clickable(
            "panel-menu-item-by-title", labels=[bookmark_title]
        )
        self.panel_ui.context_click("panel-menu-item-by-title", labels=[bookmark_title])
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

        Argument:
        expected (bool):
            If True, asserts that the toolbar is visible (collapsed="false").
            If False, asserts that the toolbar is hidden (collapsed="true")
        """

        expected_value = "false" if expected else "true"
        self.element_attribute_contains(
            self.bookmarks_toolbar, "collapsed", expected_value
        )

    #
    def set_site_autoplay_permission(
        self,
        settings: Literal["allow-audio-video", "block-audio-video", "allow-audio-only"],
    ) -> BasePage:
        """
        Open the Site audio-video permission panel and set a specific autoplay setting.

        Arguments:
            settings: "allow-audio-video" → Allow Audio and Video, "block-audio-video" → Block Audio and Video,
            "allow-audio-only" → Allow Audio but block Video
        """
        self.click_on("autoplay-icon-blocked")

        if settings == "allow-audio-video":
            self.element_clickable("permission-popup-audio-blocked")
            self.click_on("permission-popup-audio-blocked")
            self.click_and_hide_menu("allow-audio-video-menuitem")

        elif settings == "block-audio-video":
            self.element_clickable("permission-popup-audio-video-allowed")
            self.click_and_hide_menu("block-audio-video-menuitem")

        elif settings == "allow-audio-only":
            self.element_clickable("permission-popup-audio-video-allowed")
            self.click_and_hide_menu("allow-audio-only-menuitem")
        return self

    def verify_autoplay_state(self, expected: Literal["allow", "block"]) -> None:
        """Verify the current state of the autoplay permission panel and icon.
        Arguments:
            expected: "allow" → Allow Audio and Video, "block" → Block Audio and Video
        """
        if expected == "allow":
            self.element_visible("permission-popup-audio-video-allowed")
            self.element_not_visible("autoplay-icon-blocked")
        else:
            self.element_visible("permission-popup-audio-video-blocked")
            self.element_visible("autoplay-icon-blocked")

    @BasePage.context_chrome
    def expect_autoplay_blocked_icon(self, visible: bool = True) -> BasePage:
        """
        Wait for the autoplay blocked icon in the URL bar to be visible/hidden.
        Argument:
            visible: True to expect icon visible, False to expect hidden
        """
        self.element_visible("autoplay-blocked-icon", labels=[str(visible).lower()])
        return self

    @BasePage.context_chrome
    def get_status_panel_url(self) -> str:
        """
        Gets the URL displayed in the status panel at the bottom left of the browser.
        """
        self.element_visible("status-panel-label")
        status_label = self.get_element("status-panel-label")
        url = status_label.get_attribute("value")
        return url

    def verify_status_panel_url(self, expected_url: str):
        """
        Verify that the browser status panel (browser's bottom-left) contains the expected URL.
        Argument:
            expected_url: The expected URL substring to be found in the status panel
        """
        actual_url = self.get_status_panel_url()
        assert expected_url in actual_url, (
            f"Expected '{expected_url}' in status panel URL, got '{actual_url}'"
        )

    @BasePage.context_content
    def verify_domain(self, expected_domain: str) -> None:
        """
        Verify that the current URL's domain matches the expected domain using urlparse.
        This explicitly checks the domain (netloc) rather than just a substring match.
        Uses content context to get the actual page URL.

        Argument:
            expected_domain: The expected domain (e.g., "wikipedia.org", "google.com")
        """

        def _domain_matches(_):
            parsed = urlparse(self.driver.current_url)
            return expected_domain in parsed.netloc

        self.custom_wait(timeout=15).until(_domain_matches)
        parsed_url = urlparse(self.driver.current_url)
        assert expected_domain in parsed_url.netloc, (
            f"Expected '{expected_domain}' domain, got '{parsed_url.netloc}'"
        )

    @BasePage.context_chrome
    def verify_engine_returned(self, engine: str) -> None:
        """
        Verify that the given search engine is visible in the search mode switcher.
        """
        engine_locator = self.elements["searchmode-engine"]["selectorData"].format(
            engine=engine
        )
        self.wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, engine_locator))
        )

    @BasePage.context_chrome
    def verify_https_hidden_in_address_bar(self) -> None:
        """
        Wait until the HTTPS prefix is hidden in the address bar display.
        """
        self.wait.until(
            lambda d: (
                "https" not in self.get_element("awesome-bar").get_attribute("value")
            )
        )

    @BasePage.context_chrome
    def verify_address_bar_value_prefix(self, prefix: str) -> None:
        """
        Wait until the value in the address bar starts with the given prefix.

        Args:
            prefix (str): Expected starting string (e.g., "https://").
        """
        self.wait.until(
            lambda d: (
                self.get_element("awesome-bar")
                .get_attribute("value")
                .startswith(prefix)
            )
        )

    @BasePage.context_chrome
    def verify_searchbar_engine_is_focused(self, engine: str) -> None:
        """
        Verify that the given search engine button is focused (has 'selected' attribute)
        using the dynamic 'searchbar-search-engine' locator.
        """
        engine_locator = self.elements["selected_searchbar-search-engine"][
            "selectorData"
        ].format(engine=engine)
        self.wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, engine_locator)),
            message=f"Expected '{engine}' search engine to be focused (selected), but it was not found or visible.",
        )

    @BasePage.context_chrome
    def wait_for_searchbar_suggestions(self) -> None:
        """Wait until the search suggestions dropdown is visible."""
        locator = self.elements["searchbar-suggestions"]["selectorData"]
        self.wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, locator)),
            message="Search suggestions did not appear in time.",
        )

    @BasePage.context_chrome
    def verify_engine_visibility_in_searchbar_suggestion(
        self,
        term: str,
        engine_name: str,
        expected_state: Literal["visible", "not_visible"],
    ):
        """
        Type into the search bar and verify if a search engine suggestion is shown or not.
        Arguments:
            term: Search term to type in the search bar.
            engine_name: The search engine to check (e.g., "DuckDuckGo").
            expected_state: Expected visibility state of the engine ("visible" or "not_visible")
        """
        self.type_in_search_bar(term)
        if expected_state == "visible":
            self.element_visible("searchbar-search-engine", labels=[engine_name])
        else:
            self.element_not_visible("searchbar-search-engine", labels=[engine_name])

    @BasePage.context_chrome
    def add_search_bar_to_toolbar(self) -> BasePage:
        """
        Add the search bar to the toolbar via customize mode.
        """

        self.panel_ui.open_panel_menu()
        self.panel_ui.navigate_to_customize_toolbar()
        self.customize.add_widget_to_toolbar("search-bar")
        return self

    @BasePage.context_chrome
    def click_exit_button_searchmode(self) -> None:
        """
        Click the 'Exit' button in the search mode.
        Waits until the button is visible and clickable before performing the click.
        """
        # Wait until the element is visible and clickable
        self.expect(lambda _: self.get_element("exit-button-searchmode").is_displayed())

        # Click the button
        self.get_element("exit-button-searchmode").click()

    @BasePage.context_chrome
    def type_and_verify(
        self,
        input_text: str,
        expected_text: str,
        timeout: float = 5.0,
        click: bool = True,  # If True: click match; else: return index
    ) -> int | bool:
        """
        Types into the awesome bar, waits for a suggestion containing `expected_text`.

        If `click=True` (default):
            - Click the matching element and return True
            - Raises if not found (test fails)

        If `click=False`:
            - Return the 0-based index of the matching element
            - Raises if not found (test fails)
        """

        # Reset + type
        self.clear_awesome_bar()
        self.type_in_awesome_bar(input_text)

        def find_match(driver):
            suggestions = self.get_all_children("results-dropdown")

            for index, s in enumerate(suggestions):
                try:
                    if expected_text in s.text:
                        return (s, index)
                except StaleElementReferenceException:
                    continue

            return False  # keep polling

        # No try/except here — failure = real failure
        element, index = self.custom_wait(timeout=timeout).until(find_match)

        if click:
            element.click()
            return True

        return index

    @BasePage.context_chrome
    def verify_autofill_adaptive_element(
        self, expected_type: str, expected_url: str
    ) -> BasePage:
        """
        Verify that the adaptive history autofill element has the expected type and URL text.
        This method handles chrome context switching internally.
        Arguments:
            expected_type: Expected type attribute value
            expected_url: Expected URL fragment to be contained in the element text
        """
        autofill_element = self.get_element("search-result-autofill-adaptive-element")
        actual_type = autofill_element.get_attribute("type")
        actual_text = autofill_element.text

        assert actual_type == expected_type
        assert expected_url in actual_text

        return self

    @BasePage.context_chrome
    def verify_no_autofill_adaptive_elements(self) -> BasePage:
        autofill_elements = self.get_elements("search-result-autofill-adaptive-element")
        if autofill_elements:
            logging.warning(
                f"Unexpected adaptive autofill elements found: {[el.text for el in autofill_elements]}"
            )
        assert len(autofill_elements) == 0, (
            "Adaptive history autofill suggestion was not removed after deletion."
        )
        return self

    @BasePage.context_chrome
    def verify_autofill_adaptive_element(
        self, expected_type: str, expected_url: str
    ) -> BasePage:
        """
        Verify that the adaptive history autofill element has the expected type and URL text.
        This method handles chrome context switching internally.
        Arguments:
            expected_type: Expected type attribute value
            expected_url: Expected URL fragment to be contained in the element text
        """
        autofill_element = self.get_element("search-result-autofill-adaptive-element")
        actual_type = autofill_element.get_attribute("type")
        actual_text = autofill_element.text

        assert actual_type == expected_type
        assert expected_url in actual_text

        return self

    @BasePage.context_chrome
    def verify_no_autofill_adaptive_elements(self) -> BasePage:
        """Verify that no adaptive history autofill elements are present."""
        autofill_elements = self.get_elements("search-result-autofill-adaptive-element")
        if autofill_elements:
            logging.warning(
                f"Unexpected adaptive autofill elements found: {[el.text for el in autofill_elements]}"
            )
        assert len(autofill_elements) == 0, (
            "Adaptive history autofill suggestion was not removed after deletion."
        )
        return self

    @BasePage.context_chrome
    def expect_container_label(self, label_expected: str):
        """
        Verify the container label for user context (container tabs).
        Argument:
            label_expected: The expected label text for the user context container.
        """
        actual_label = self.get_element("tab-container-label").text
        assert actual_label == label_expected

    @BasePage.context_chrome
    def click_back_button(self) -> None:
        """
        Click the 'Back' button.
        Waits until the button is visible and clickable before performing the click.
        """
        # Wait until the element is visible and clickable
        self.expect(lambda _: self.get_element("back-button").is_displayed())

        # Click the button
        self.get_element("back-button").click()

    @BasePage.context_chrome
    def get_library_recently_closed_urls(self, history_open: bool = False):
        """
        Navigate through Library > History > Recently Closed Tabs and extract URLs. This navigates a chain of nested
        XUL panel submenus. Each submenu transition updates a 'visible' attribute on the target panelview,
        but the DOM elements persist (they're just marked offscreen). We must wait for the correct panel state and
        exclude offscreen duplicates when querying.
        Argument:
            history_open: If True, assumes Library > History is already open.
        """
        if not history_open:
            self.open_library_history_submenu()

        # Click "Recently Closed Tabs" to open the third-level submenu.
        self._click_with_fallbacks(
            lambda: self.get_element("toolbar-history-recently-closed-tabs"),
            name="Recently closed tabs button",
        )

        # Wait for the recentlyClosedTabs panel to become visible.
        # Firefox sets visible='true' on the active panelview; previous panels stay in DOM but are marked offscreen.
        self.wait.until(
            lambda d: d.find_elements(
                By.XPATH,
                self.XPATH_LIBRARY_RECENTLY_CLOSED_TABS_VIEW_VISIBLE,
            )
        )

        # Extract closed tab items - each has a targetURI attribute with the page URL
        items = self.wait.until(
            lambda d: self.get_elements("library-recently-closed-tabs-items")
        )
        urls = {
            uri for item in items if (uri := self._get_target_uri(item)) is not None
        }

        # Close the panel chain (two ESC presses to exit nested submenus)
        self.actions.send_keys(Keys.ESCAPE).send_keys(Keys.ESCAPE).perform()
        return urls

    @BasePage.context_chrome
    def open_library_history_submenu(self) -> BasePage:
        """
        Open the Library > History submenu from the toolbar.

        The Library button (when added to toolbar) opens a widget panel that uses
        Firefox's PanelMultiView system. Clicking "History" navigates to a subview
        (PanelUI-history) within the same panel container.

        XUL panel elements don't always respond to standard Selenium clicks due to
        how Firefox handles focus and event dispatch in chrome UI. We use fallback
        click methods and wait for specific panel states rather than simple visibility.
        """
        # Open the Library panel - this creates/shows the panel container
        self.click_on("library-button")

        # Wait for any panel to be marked open (panelopen='true' is set on the panel element)
        self.wait.until(lambda d: d.find_elements(By.XPATH, self.XPATH_PANEL_OPEN))

        # Navigate to History subview within the Library panel
        self.element_clickable("library-history-submenu-button")
        self._click_with_fallbacks(
            lambda: self.get_element("library-history-submenu-button"),
            name="Library history submenu",
        )

        # Wait for the History panel content to be available (not just visible, but not offscreen).
        # Firefox keeps previous panel content in DOM but marks ancestors with 'offscreen' class.
        self.wait.until(
            lambda d: d.find_elements(
                By.XPATH,
                self.XPATH_RECENTLY_CLOSED_TABS_NOT_OFFSCREEN,
            )
        )
        self.element_visible("toolbar-history-recently-closed-tabs")
        return self

    def _click_with_fallbacks(
        self, get_el: Callable[[], WebElement], *, name: str = "element"
    ):
        """
        Attempt to click an element using multiple strategies.
        XUL toolbar buttons in Firefox chrome UI don't always respond to standard
        click events due to focus handling and event dispatch differences. This tries:
          1. ActionChains move + click (works when element needs focus first)
          2. Direct element.click() (standard approach)
          3. Send ENTER key (keyboard activation fallback)
        Argumnets:
            get_el: Callable that returns the WebElement to click (called fresh each
                    attempt in case of stale element issues).
            name: Human-readable name for error messages.
        """
        last_exc = None
        attempts = ("actionchains", "direct_click", "enter_key")
        for attempt in attempts:
            try:
                el = get_el()
                if attempt == "actionchains":
                    ActionChains(self.driver).move_to_element(el).click().perform()
                elif attempt == "direct_click":
                    el.click()
                else:
                    el.send_keys(Keys.ENTER)
                return
            except (InvalidSessionIdException, NoSuchWindowException):
                raise
            except WebDriverException as exc:
                last_exc = exc
        raise last_exc or RuntimeError(f"Failed to click {name}")

    def _get_target_uri(self, el: WebElement):
        """
        Extract the targetURI attribute from a closed tab list item.

        Tries standard attribute access first, falls back to regex on outerHTML
        if the attribute isn't directly accessible (can happen with XUL elements).
        """
        uri = el.get_attribute("targetURI") or el.get_attribute("targeturi")
        if uri:
            return uri
        html = el.get_attribute("outerHTML") or ""
        match = self._TARGET_URI_RE.search(html)
        return match.group(1) if match else None

    @BasePage.context_chrome
    def perform_download_context_action(self, action_name: str) -> BasePage:
        """
        From the downloads panel, right-click the latest download and perform a context menu action.

        :param action_name: The key for the context menu action, e.g.,
            "context-menu-delete" or "context-menu-always-open-similar-files"
        """
        downloads_button = self.get_download_button()
        downloads_button.click()

        # Locate the latest download item
        download_item = self.get_element("download-panel-item")

        # Right-click and select the desired action
        self.context_click(download_item)
        self.context_menu.get_element(action_name).click()
        self.context_menu.hide_popup_by_child_node(action_name)

        return self

    @BasePage.context_chrome
    def open_downloaded_file(self) -> None:
        """
        Opens the most recently downloaded file from the Downloads panel.
        """
        # Wait until the element is visible and clickable
        self.expect(
            lambda _: self.get_element("download-target-element").is_displayed()
        )

        # Click the button
        self.get_element("download-target-element").click()

    @BasePage.context_chrome
    def open_download_panel(self):
        """
        Open the download panel.
        """
        self.click_on("downloads-button")
        return self

    @BasePage.context_chrome
    def is_download_button_visible(self) -> bool:
        """
        Returns True if the Downloads button is visible, False otherwise.
        """
        try:
            return self.get_element("downloads-button").is_displayed()
        except Exception:
            # Element not found or not accessible
            return False
