from pypom import Page
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

from modules.page_base import BasePage


class Navigation(BasePage):
    """Page Object Model for nav buttons and AwesomeBar"""

    URL_TEMPLATE = "about:blank"
    BROWSER_MODES = {
        "Bookmarks": "*",
        "Tabs": "%",
        "History": "^",
        "Actions": ">",
    }

    _xul_source_snippet = (
        'xmlns:xul="http://www.mozilla.org/keymaster/gatekeeper/there.is.only.xul"'
    )

    def ensure_chrome_context(self):
        """Make sure the Selenium driver is using CONTEXT_CHROME"""
        if self._xul_source_snippet not in self.driver.page_source:
            self.driver.set_context(self.driver.CONTEXT_CHROME)

    def resume_content_context(self):
        """Make sure the Selenium driver is using CONTEXT_CONTENT"""
        if self._xul_source_snippet in self.driver.page_source:
            self.driver.set_context(self.driver.CONTEXT_CONTENT)

    def expect_in_content(self, condition) -> Page:
        """Like BasePage.expect, but guarantee we're looking at CONTEXT_CONTENT"""
        with self.driver.context(self.driver.CONTEXT_CONTENT):
            self.expect(condition)
        return self

    def set_awesome_bar(self) -> Page:
        """Set the awesome_bar attribute of the Navigation object"""
        self.ensure_chrome_context()
        self.awesome_bar = self.get_element("awesome-bar")
        return self

    def get_awesome_bar(self) -> WebElement:
        """Get the Awesome Bar. Prefer this over get_element."""
        self.set_awesome_bar()
        return self.awesome_bar

    def clear_awesome_bar(self) -> Page:
        """Clear the Awesome Bar. Prefer this over get_element("awesome-bar").clear()"""
        self.set_awesome_bar()
        self.awesome_bar.clear()
        return self

    def type_in_awesome_bar(self, term: str) -> Page:
        """Enter text into the Awesome Bar. You probably want self.search()"""
        self.set_awesome_bar()
        self.awesome_bar.click()
        self.awesome_bar.send_keys(term)
        return self

    def set_search_mode_via_awesome_bar(self, mode: str) -> Page:
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

    def search(self, term: str, mode=None) -> Page:
        """
        Search using the Awesome Bar, optionally setting the search mode first. Returns self.

        Parameters
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

    def click_in_awesome_bar(self) -> Page:
        """
        Focuses and clicks on the Awesome Bar. This method is a utility to focus the input area
        of the Awesome Bar without typing any text. Useful for setting up subsequent interactions.

        Returns:
            Page: An instance of itself to support method chaining.
        """
        self.set_awesome_bar()  # Ensures the Awesome Bar is set up and focused
        self.awesome_bar.click()  # Performs a click action on the Awesome Bar
        return self

    def click_on_onoff_search_button(self, identifier: str, index: int = 0) -> Page:
        """
        Clicks on a specific search engine button located in the Awesome Bar based on the given identifier.
        It can handle special site identifiers that have custom names like 'Amazon' or 'Wikipedia'.

        Parameters:
            identifier (str): The name or special identifier of the search engine.
            index (int): The index of the button among multiple ones (default is 0 for the first button).

        Returns:
            Page: An instance of itself to support method chaining.

        Notes:
            This method focuses on the Awesome Bar first to ensure that search engine buttons are ready
            for interaction. It constructs a unique CSS selector to find the button and ensures the button
            is visible before clicking.
        """
        # Maps special identifiers to their common names on the UI
        special_sites = {
            "Amazon": "Amazon.com",
            "Wikipedia": "Wikipedia (en)"
        }

        # Ensure the Awesome Bar is focused to interact with search engine buttons
        self.click_in_awesome_bar()

        # Prepare the selector based on identifier, special cases are handled
        index = "engine-" + str(index)
        key = "search-engine-buttons"
        handle = identifier.lower()
        if identifier in special_sites:
            identifier = special_sites[identifier]  # Map to special name if exists

        # Build the selector using the identifier and index
        button_selector = self.get_selector(key, index, identifier, handle)

        # Wait for the button to be visible and then click it
        self.wait.until(
            EC.visibility_of_element_located(button_selector)
        )
        self.driver.find_element(*button_selector).click()
        return self