import logging
import os
import re

from pypom import Page
from selenium.common.exceptions import (
    StaleElementReferenceException,
    WebDriverException,
)
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from modules.page_base import BasePage
from modules.util import BrowserActions


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
        self.set_content_context()
        self.driver.get("about:config")
        self.expect(EC.title_contains("Advanced Preferences"))
        searchbar = self.get_element("about-config-search-input")
        searchbar.clear()
        searchbar.send_keys(term + Keys.ENTER)
        return self

    def toggle_true_false_config(self, term: str) -> BasePage:
        """
        Main method to toggle a true false pref in about:config
        Note: To use this in a test, use pref_list - ("browser.aboutConfig.showWarning", False),
        in the test suite's conftest.py or use add_to_prefs_list fixture in the test itself
        """
        self.search_pref(term)
        toggle_tf_button = self.get_element("value-edit-button")
        toggle_tf_button.click()
        return self

    def change_config_value(self, term: str, value) -> BasePage:
        """
        Main method to change a config's value in about:config
        Note: To use this in a test, use pref_list - ("browser.aboutConfig.showWarning", False),
        in the test suite's conftest.py or use add_to_prefs_list fixture in the test itself.
        """
        self.search_pref(term)
        pref_edit_button = self.get_element("value-edit-button")
        pref_edit_button.click()
        pref_edit = self.get_element("value-edit-field")
        pref_edit.send_keys(value)
        pref_edit_button.click()
        return self


class AboutDownloads(BasePage):
    """
    The POM for the about:downloads page

    Attributes
    ----------
    driver: selenium.webdriver.Firefox
        WebDriver object under test
    """

    URL_TEMPLATE = "about:downloads"

    def is_empty(self) -> bool:
        """Checks to see if downloads page is empty"""
        found = False
        try:
            self.element_visible("no-downloads-label")
            found = True
        finally:
            return found

    def get_downloads(self) -> list:
        """Get all download targets"""
        return self.get_elements("download-target")

    def wait_for_num_downloads(self, num: int) -> BasePage:
        """Wait for the number of downloads to equal num"""
        self.expect(lambda _: len(self.get_downloads()) == num)
        return self


class AboutGlean(BasePage):
    """
    Page Object Model for about:glean

    Attributes
    ----------
    driver: selenium.webdriver.Firefox
        WebDriver object under test
    """

    URL_TEMPLATE = "about:glean"

    def change_ping_id(self, ping_id: str) -> Page:
        """
        Change the Glean ping id to the given string.
        """
        ba = BrowserActions(self.driver)
        self.click_on("manual-testing")
        ping_input = self.get_element("ping-id-input")
        ba.clear_and_fill(ping_input, ping_id)
        self.wait.until(
            EC.text_to_be_present_in_element(
                self.get_selector("ping-submit-label"), ping_id
            )
        )
        self.get_element("ping-submit-button").click()
        return self


class AboutLogins(BasePage):
    """
    Page Object Model for about:logins, which goes through Shadow DOMs.

    Attributes
    ----------
    driver: selenium.webdriver.Firefox
        WebDriver object under test
    """

    URL_TEMPLATE = "about:logins"

    def click_add_login_button(self) -> Page:
        """Click the Add Login button"""
        self.get_element("create-login-button").click()
        logging.info("Clicked add login button")
        return self

    def create_new_login(self, form_info: dict) -> Page:
        """
        Given a dict with keys that match the valid item types in the
        new login dialog, create a new login with those values through UI.
        """
        ba = BrowserActions(self.driver)
        try:
            for item_type, value in form_info.items():
                logging.info(f"Filling {item_type} with {value}")
                ba.clear_and_fill(
                    self.get_element("login-item-type", labels=[item_type]), value
                )
            logging.info("Clicking submit...")
            self.get_element("create-login-button")
            logging.info("Submitted.")
        except (WebDriverException, StaleElementReferenceException):
            logging.info("Element not found or stale, pressing 'Save Changes'")
            self.get_element("save-changes-button").click()
            logging.info("Pressed.")
        return self

    def check_logins_present(
        self, actual_logins: dict, expected_logins: dict, check_password=False
    ):
        """
        Checks that all logins expected are present in the list of elements
        ----
        logins: {"username@website": "password"}
            Example:
            username: hello, website: mozilla.social, password: pwpwpwpw
            logins = {"hello@mozilla.social": "pwpwpwpw}
        """
        # Check that all created logins are here
        if not check_password:
            for login in expected_logins.keys():
                assert login in actual_logins
        else:
            assert expected_logins == actual_logins

    def remove_password_csv(self, downloads_dir):
        # Delete password.csv, if there is one in the export location
        passwords_csv = os.path.join(downloads_dir, "passwords.csv")
        for file in os.listdir(downloads_dir):
            delete_files_regex = re.compile(r"\bpasswords.csv\b")
            if delete_files_regex.match(file):
                os.remove(passwords_csv)


class AboutPrivatebrowsing(BasePage):
    """
    POM for about:privatebrowsing page
    """

    URL_TEMPLATE = "about:privatebrowsing"


class AboutProfiles(BasePage):
    """
    POM for about:profiles page
    """

    URL_TEMPLATE = "about:profiles"


class AboutTelemetry(BasePage):
    """
    The POM for the about:telemetry page
    """

    URL_TEMPLATE = "about:telemetry"


class AboutNetworking(BasePage):
    """
    POM for about:networking page
    """

    URL_TEMPLATE = "about:networking"

    def select_network_category(self, option: str):
        """
        Clicks the corresponding sidebar tab in the about:networking page.
        """
        # Use dynamic ID based on the option name
        self.get_element("networking-sidebar-category", labels=[option]).click()
