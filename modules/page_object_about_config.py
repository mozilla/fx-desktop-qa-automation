from selenium.webdriver.common.keys import Keys

from modules.page_base import BasePage


class AboutConfig(BasePage):
    """
    The POM for the about:config page

    Attributes
    ----------
    driver: selenium.webdriver.Firefox
        WebDriver object under test
    """

    URL_TEMPLATE = "about:config"

    def click_warning_button(self) -> BasePage:
        self.get_element("warning-button").click()
        return self

    def search_pref(self, term: str) -> BasePage:
        searchbar = self.get_element("about-config-search-input")
        searchbar.clear()
        searchbar.send_keys(term + Keys.ENTER)
        return self
