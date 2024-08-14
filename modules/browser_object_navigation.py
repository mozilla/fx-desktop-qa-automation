import logging

from time import sleep
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

from modules.classes.bookmark import Bookmark
from modules.page_base import BasePage
from modules.util import BrowserActions, Utilities

class Navigation(BasePage):
    """Page Object Model for nav buttons and AwesomeBar"""

    URL_TEMPLATE = "about:blank"
    BROWSER_MODES = {
        "Bookmarks": "*",
        "Tabs": "%",
        "History": "^",
        "Actions": ">",
    }

    def expect_in_content(self, condition) -> BasePage:
        """Like BasePage.expect, but guarantee we're looking at CONTEXT_CONTENT"""
        with self.driver.context(self.driver.CONTEXT_CONTENT):
            self.wait.until(condition)
        return self

    def set_awesome_bar(self) -> BasePage:
        """Set the awesome_bar attribute of the Navigation object"""
        self.set_chrome_context()
        self.awesome_bar = self.get_element("awesome-bar")
        return self

    def get_awesome_bar(self) -> WebElement:
        """Get the Awesome Bar. Prefer this over get_element."""
        self.set_awesome_bar()
        return self.awesome_bar

    def get_awesome_bar_text(self):
        """
        Get the text directly from the awesome bar.
        This is different from 'driver.current_url' which pulls from href
        """
        self.set_chrome_context()
        awesome_bar = self.get_element("awesome-bar").get_attribute("value")
        return awesome_bar

    def clear_awesome_bar(self) -> BasePage:
        """Clear the Awesome Bar. Prefer this over get_element("awesome-bar").clear()"""
        self.set_awesome_bar()
        self.awesome_bar.clear()
        return self

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
        with self.driver.context(self.driver.CONTEXT_CHROME):
            if mode:
                self.set_search_mode_via_awesome_bar(mode).type_in_awesome_bar(
                    term + Keys.ENTER
                )
            else:
                self.type_in_awesome_bar(term + Keys.ENTER)
        return self

    def set_search_bar(self) -> BasePage:
        """Set the search_bar attribute of the Navigation object"""
        self.set_chrome_context()
        self.search_bar = self.find_element(By.CLASS_NAME, "searchbar-textbox")
        return self

    def search_bar_search(self, term: str) -> BasePage:
        """
        Search using the *Old* Search Bar. Returns self.

        Attributes
        ----------

        term : str
            The search term
        """
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.search_bar = self.find_element(By.CLASS_NAME, "searchbar-textbox")
            self.search_bar.click()
            self.search_bar.send_keys(term + Keys.ENTER)
        return self

    def type_in_search_bar(self, term: str) -> BasePage:
        """
        Type in the *Old* Search Bar. Returns self.

        Attributes
        ----------

        term : str
            The search term
        """
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.search_bar = self.find_element(By.CLASS_NAME, "searchbar-textbox")
            self.search_bar.click()
            self.search_bar.send_keys(term)
        return self

    def click_on_change_search_settings_button(self) -> BasePage:
        with self.driver.context(self.driver.CONTEXT_CHROME):
            self.search_bar = self.find_element(By.CLASS_NAME, "searchbar-textbox")
            self.search_bar.click()
            self.change_search_settings_button = self.find_element(
                By.ID, "searchbar-anon-search-settings"
            )
            self.change_search_settings_button.click()
        return self

    def click_in_awesome_bar(self) -> BasePage:
        self.set_awesome_bar()
        self.awesome_bar.click()
        return self

    def get_download_button(self) -> BasePage:
        """
        Gets the download button WebElement
        """
        downloads_button = None
        with self.driver.context(self.driver.CONTEXT_CHROME):
            downloads_button = self.get_element("downloads-button")
            return downloads_button

    def wait_for_download_animation_finish(
        self, downloads_button: WebElement
    ) -> BasePage:
        """
        Waits for the download button to finish playing the animation for downloading to local computer
        """
        with self.driver.context(self.driver.CONTEXT_CHROME):
            try:
                self.wait.until(
                    lambda _: downloads_button.get_attribute("notification") == "finish"
                )
            except TimeoutException:
                logging.warning("Animation did not finish or did not play.")

    def open_tracker_panel(self) -> BasePage:
        """
        Clicks the shield icon and opens the panel associated with it
        """
        with self.driver.context(self.context_id):
            self.get_element("shield-icon").click()
            return self

    def bookmark_page_other(self) -> BasePage:
        with self.driver.context(self.context_id):
            self.get_element("star-button").click()
            dropdown = self.get_element("bookmarks-type-dropdown")
            dropdown.click()
            self.get_element("bookmarks-type-dropdown-other").click()
            dropdown.click()
            self.get_element("save-bookmark-button").click()

    def add_bookmark_advanced(self, bookmark_data: Bookmark, ba: BrowserActions) -> BasePage:
        with self.driver.context(self.context_id):
            iframe = self.get_element("bookmark-iframe")
            ba.switch_to_iframe_context(iframe)
            Utilities().write_html_content("now", self.driver, True)
            sleep(5)
            if bookmark_data.name is not None:
            # fill name
                self.get_element("new-bookmark-name-field").send_keys(bookmark_data.name)
            # fill url
            self.get_element("new-bookmark-url-field").send_keys(bookmark_data.url)
            # fill tags
            if bookmark_data.tags is not None:
                self.get_element("new-bookmark-tags-field").send_keys(bookmark_data.tags)
            # fill keywords
            if bookmark_data.keyword is not None:
                self.get_element("new-bookmark-keyword-field").send_keys(
                    bookmark_data.keyword
                )
            self.get_element("bookmark-accept-button").click()
            ba.switch_to_content_context()
