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

    def expect_in_content(self, condition) -> BasePage:
        """Like BasePage.expect, but guarantee we're looking at CONTEXT_CONTENT"""
        with self.driver.context(self.driver.CONTEXT_CONTENT):
            self.expect(condition)
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
