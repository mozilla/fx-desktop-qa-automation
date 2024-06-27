from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

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

    def search_pref(self, term: str) -> BasePage:
        searchbar = self.get_element("about-config-search-input")
        searchbar.clear()
        searchbar.send_keys(term + Keys.ENTER)
        return self

    def toggle_true_false(self) -> BasePage:
        toggle_tf_button = self.find_element(By.CLASS_NAME, "cell-edit")
        toggle_tf_button.click()
        return self

    def toggle_true_false_config(self, term: str) -> BasePage:
        """
        Main method to toggle a true false pref in about:config
        """
        self.set_content_context()
        self.driver.get("about:config")
        self.expect(EC.title_contains("Advanced Preferences"))
        self.search_pref(term)
        self.toggle_true_false()
        return self
