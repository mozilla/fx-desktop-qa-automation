import logging

from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

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

    def __init__(self, driver: Firefox, **kwargs):
        super().__init__(driver, **kwargs)
        self.search_bar = None
        self.change_search_settings_button = None

    @BasePage.content_context
    def expect_in_content(self, condition) -> BasePage:
        """Like BasePage.expect, but guarantee we're looking at CONTEXT_CONTENT"""
        self.wait.until(condition)
        return self

    @BasePage.chrome_context
    def set_awesome_bar(self) -> BasePage:
        """Set the awesome_bar attribute of the Navigation object"""
        self.awesome_bar = self.get_element("awesome-bar")
        return self

    @BasePage.chrome_context
    def get_awesome_bar(self) -> WebElement:
        """Get the Awesome Bar. Prefer this over get_element."""
        self.set_awesome_bar()
        return self.awesome_bar

    @BasePage.chrome_context
    def get_awesome_bar_text(self):
        """
        Get the text directly from the awesome bar.
        This is different from 'driver.current_url' which pulls from href
        """
        awesome_bar = self.get_element("awesome-bar").get_attribute("value")
        return awesome_bar

    @BasePage.chrome_context
    def clear_awesome_bar(self) -> BasePage:
        """Clear the Awesome Bar. Prefer this over get_element("awesome-bar").clear()"""
        self.set_awesome_bar()
        self.awesome_bar.clear()
        return self

    @BasePage.chrome_context
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

    @BasePage.chrome_context
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

    @BasePage.chrome_context
    def set_search_bar(self) -> BasePage:
        """Set the search_bar attribute of the Navigation object"""
        self.search_bar = self.find_element(By.CLASS_NAME, "searchbar-textbox")
        return self

    @BasePage.chrome_context
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

    @BasePage.chrome_context
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

    @BasePage.chrome_context
    def click_on_change_search_settings_button(self) -> BasePage:
        self.search_bar = self.find_element(By.CLASS_NAME, "searchbar-textbox")
        self.search_bar.click()
        self.change_search_settings_button = self.find_element(
            By.ID, "searchbar-anon-search-settings"
        )
        self.change_search_settings_button.click()
        return self

    @BasePage.chrome_context
    def click_in_awesome_bar(self) -> BasePage:
        self.set_awesome_bar()
        self.awesome_bar.click()
        return self

    @BasePage.chrome_context
    def get_download_button(self) -> WebElement:
        """
        Gets the download button WebElement
        """
        downloads_button = self.get_element("downloads-button")
        return downloads_button

    @BasePage.chrome_context
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

    @BasePage.chrome_context
    def open_tracker_panel(self) -> BasePage:
        """
        Clicks the shield icon and opens the panel associated with it
        """
        self.get_element("shield-icon").click()
        return self

    @BasePage.chrome_context
    def bookmark_page_other(self) -> BasePage:
        self.get_element("star-button").click()
        dropdown = self.get_element("bookmarks-type-dropdown")
        dropdown.click()
        self.get_element("bookmarks-type-dropdown-other").click()
        dropdown.click()
        self.get_element("save-bookmark-button").click()
        return self

    @BasePage.chrome_context
    def add_bookmark_advanced(
        self, bookmark_data: Bookmark, ba: BrowserActions
    ) -> BasePage:
        iframe = self.get_element("bookmark-iframe")
        ba.switch_to_iframe_context(iframe)
        # fill name
        if bookmark_data.name is not None:
            self.actions.send_keys(bookmark_data.name).perform()
        self.actions.send_keys(Keys.TAB).perform()
        # fill url
        self.actions.send_keys(bookmark_data.url + Keys.TAB).perform()
        # fill tags
        if bookmark_data.tags is not None:
            self.actions.send_keys(bookmark_data.tags).perform()
        self.actions.send_keys(Keys.TAB).perform()
        # fill keywords
        if bookmark_data.keyword is not None:
            self.actions.send_keys(bookmark_data.keyword).perform()
        self.actions.send_keys(Keys.TAB, Keys.TAB, Keys.TAB, Keys.ENTER).perform()
        ba.switch_to_content_context()
        return self

    @BasePage.chrome_context
    def add_bookmark_via_star(self) -> BasePage:
        """
        Bookmark a site via star button and click save on the bookmark panel
        """
        self.get_element("star-button").click()
        self.get_element("save-bookmark-button").click()
        return self

    @BasePage.chrome_context
    def add_bookmark_via_menu(self) -> BasePage:
        """
        Bookmark a site via bookmarks menu and click save on the bookmark panel
        """

        self.get_element("bookmark-current-tab").click()
        self.get_element("save-bookmark-button").click()
        return self

    @BasePage.chrome_context
    def toggle_bookmarks_toolbar_with_key_combo(self) -> BasePage:
        """Use Cmd/Ctrl + B to open the Print Preview, wait for load"""

        if self.sys_platform() == "Darwin":
            mod_key = Keys.COMMAND
        else:
            mod_key = Keys.CONTROL
        self.perform_key_combo(mod_key, Keys.SHIFT, "b")
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

    @BasePage.chrome_context
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

    @BasePage.chrome_context
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
