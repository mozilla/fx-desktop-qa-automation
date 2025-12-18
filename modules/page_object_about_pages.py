import logging
import os
import re

from pypom import Page
from selenium.common.exceptions import (
    StaleElementReferenceException,
    WebDriverException,
)
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from modules.page_base import BasePage
from modules.page_object_generics import GenericPage
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

    def enable_metrics_table(self) -> Page:
        """
        Enable experimental features and open the Metrics Table category.
        """
        self.element_clickable("enable-new-features")
        self.click_on("enable-new-features")
        self.element_clickable("metrics-table-category")
        self.click_on("metrics-table-category")
        return self

    def filter_metrics(self, filter_term: str) -> Page:
        """
        Filter metrics in the Metrics Table by the given term.
        """
        filter_input = self.get_element("filter-metrics-input")
        filter_input.clear()
        filter_input.send_keys(filter_term)
        return self

    def load_metric(self, metric_name: str) -> Page:
        """
        Click the load button for a specific metric row.
        """
        self.element_clickable("metric-row-load-button", labels=[metric_name])
        self.click_on("metric-row-load-button", labels=[metric_name])
        return self

    def get_metric_timeline_events(self, metric_name: str, timeout: int = 30) -> list:
        """
        Get all timeline event elements for a specific metric.
        Returns a list of event <g> elements from the SVG timeline.

        Args:
            metric_name: The metric identifier (e.g., "serp.impression")
            timeout: Max seconds to wait for events to appear (default 30)
        """
        self.custom_wait(timeout=timeout).until(
            lambda _: len(
                self.get_elements("metric-timeline-events", labels=[metric_name])
            )
            > 0
        )
        return self.get_elements("metric-timeline-events", labels=[metric_name])

    def get_metric_value_text(self, metric_name: str) -> str:
        """
        Get the text content from the value cell of a metric row.
        Waits until JSON-like content is present.
        """

        def value_contains_json(_):
            el = self.get_element("metric-value-cell", labels=[metric_name])
            txt = el.text.strip()
            return txt if ("{" in txt and "}" in txt) else None

        return self.wait.until(value_contains_json)

    def get_metric_event_count(self, metric_name: str) -> int:
        """
        Get the current number of timeline events for a metric.
        Returns 0 if no events are found.
        """
        try:
            events = self.get_elements("metric-timeline-events", labels=[metric_name])
            return len(events) if events else 0
        except Exception:
            return 0

    def click_newest_metric_event(self, metric_name: str) -> Page:
        """
        Click the newest (last) event dot in the metric's timeline.
        Clicks the circle inside the <g> element to avoid SVG click flakiness.
        """
        from selenium.webdriver.common.by import By

        events = self.get_metric_timeline_events(metric_name)
        newest_event = events[-1]
        newest_event.find_element(By.CSS_SELECTOR, "circle").click()
        return self

    def wait_for_new_metric_event(
        self, metric_name: str, previous_count: int, timeout: int = 15
    ) -> Page:
        """
        Wait until the metric has more events than the previous count.
        """
        self.custom_wait(timeout=timeout).until(
            lambda _: self.get_metric_event_count(metric_name) > previous_count
        )
        return self

    def get_metric_payload(self, metric_name: str) -> dict:
        """
        Get the parsed JSON payload from a metric's value cell.

        Returns:
            dict: The parsed JSON payload, or empty dict if parsing fails.
        """
        import json

        raw_text = self.get_metric_value_text(metric_name)

        start = raw_text.find("{")
        end = raw_text.rfind("}")

        if start == -1 or end == -1 or end <= start:
            return {}

        json_str = raw_text[start : end + 1]
        return json.loads(json_str)

    def poll_glean_metric(
        self, metric_path: str, timeout: int = 15, poll_interval: float = 0.5
    ) -> list:
        """
        Poll a Glean metric via JS API until data is available.

        Args:
            metric_path: Dot-separated path like "serp.impression"
            timeout: Max seconds to wait
            poll_interval: Seconds between polls

        Returns:
            list: The metric events/values from testGetValue()
        """
        import time

        js_code = f"""
            try {{
                let parts = "{metric_path}".split(".");
                let obj = Glean;
                for (let p of parts) {{
                    obj = obj[p];
                }}
                return obj.testGetValue() || [];
            }} catch(e) {{
                return [];
            }}
        """

        end_time = time.time() + timeout
        with self.driver.context(self.driver.CONTEXT_CHROME):
            while time.time() < end_time:
                result = self.driver.execute_script(js_code)
                if result and len(result) > 0:
                    return result
                time.sleep(poll_interval)

        return []


class AboutLogins(BasePage):
    """
    Page Object Model for about:logins, which goes through Shadow DOMs.

    Attributes
    ----------
    driver: selenium.webdriver.Firefox
        WebDriver object under test
    """

    URL_TEMPLATE = "about:logins"

    def __init__(self, driver: Firefox, **kwargs):
        super().__init__(driver, **kwargs)
        self.ba = BrowserActions(self.driver)

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
        try:
            for item_type, value in form_info.items():
                logging.info(f"Filling {item_type} with {value}")
                self.fill("login-item-type", value, labels=[item_type])
            logging.info("Clicking submit...")
            self.wait.until(
                lambda _: self.get_element("create-login-button").get_attribute(
                    "disabled"
                )
                is None
            )
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

    def verify_csv_export(
        self, downloads_folder: str, filename: str, timeout: int = 20
    ):
        """
        Wait until the exported CSV file is present, non-empty, and readable.
        """
        csv_file = os.path.join(downloads_folder, filename)

        def file_ready(_):
            # Check if the file path exists. If not, continue
            if not os.path.exists(csv_file):
                return False
            try:
                # Verify that the file isn't empty
                if os.path.getsize(csv_file) == 0:
                    return False

                # Attempt to read a few bytes to ensure the file is unlocked
                # and readable (handles cases where the OS is still writing).
                with open(csv_file, "r", encoding="utf-8") as f:
                    f.read(10)
                return True

            except (OSError, PermissionError) as e:
                # Log and retry until timeout instead of failing immediately
                logging.debug(f"[verify_csv_export] File not ready yet: {e}")
                return False

        WebDriverWait(self.driver, timeout).until(file_ready)
        return csv_file

    def add_login(self, origin: str, username: str, password: str):
        """
        Adds a new saved login entry.

        Args:
            origin (str): The site URL (e.g., https://example.com)
            username (str): The username to save
            password (str): The password to save
        """
        self.click_add_login_button()
        self.create_new_login(
            {
                "origin": origin,
                "username": username,
                "password": password,
            }
        )

    def export_passwords_csv(self, downloads_folder: str, filename: str):
        """
        Export passwords to a CSV file and navigate the save dialog to the target location.

        Args:
            downloads_folder (str): The folder where the CSV should be saved.
            filename (str): The name of the CSV file.
        """
        # Open about:logins and click export buttons
        self.open()
        self.click_on("menu-button")
        self.click_on("export-passwords-button")
        self.click_on("continue-export-button")

        # Wait for export dialog and navigate to folder
        page = GenericPage(self.driver)
        page.navigate_dialog_to_location(downloads_folder, filename)


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

    def open_raw_json_data(self):
        """
        Opens the Raw JSON telemetry view:
          - Click Raw category
          - Switch to the new tab
          - Click the Raw Data tab
        """

        # Click "Raw" category
        self.get_element("category-raw").click()

        # Switching to the new tab opened by Raw
        self.switch_to_new_tab()

        # Click "Raw Data" tab
        self.get_element("rawdata-tab").click()


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
