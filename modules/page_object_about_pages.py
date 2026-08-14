import json
import logging
import os
from time import sleep, time
from typing import Optional

from pypom import Page
from selenium.common.exceptions import (
    NoAlertPresentException,
    StaleElementReferenceException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver import ActionChains, Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from modules.page_base import BasePage
from modules.util import BrowserActions


class AboutCache(BasePage):
    """
    POM for the about:cache page
    """

    URL_TEMPLATE = "about:cache"

    def open_disk_or_memory_cache_entries(self, storage: str = "disk"):
        """
        Open the cache entries list for the given storage type.

        Argument:
            storage: 'disk' or 'memory'
        """
        self.click_on(f"{storage}-cache-link")

    def get_entries_text(self):
        """Return the full text content of the cache entries table, lowercased."""
        return self.get_element("entries-table").text.lower()

    def get_number_of_entries(self):
        """Return the 'Number of entries' value from the about:cache overview."""
        return self.get_element("number-of-entries").text


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

    def edit_config_value(self, term: str, value) -> BasePage:
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

    def get_pref_value(self, term: str):
        """Return the current value string for a preference from about:config."""
        self.search_pref(term)
        return self.get_element("pref-cell-value").text.strip()

    def toggle_config_value(self, term: str, value) -> BasePage:
        """
        Main method to toggle a config's value in about:config
        Note: To use this in a test, use pref_list - ("browser.aboutConfig.showWarning", False),
        in the test suite's conftest.py or use add_to_prefs_list fixture in the test itself
        """
        self.search_pref(term)
        pref_edit_button = self.get_element("value-edit-button")
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


class AboutLogins(BasePage):
    """
    Page Object Model for about:logins, which goes through Shadow DOMs.

    Attributes
    ----------
    driver: selenium.webdriver.Firefox
        WebDriver object under test
    """

    URL_TEMPLATE = "about:logins"

    # Settle interval to let a native (non-DOM) prompt take keyboard focus before
    # typing OS-level keystrokes; its readiness cannot be polled directly.
    _NATIVE_PROMPT_SETTLE_S = 0.5

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
                lambda _: (
                    self.get_element("create-login-button").get_attribute("disabled")
                    is None
                )
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

    def remove_password_csv(self, downloads_dir, filename: str = "passwords.csv"):
        # Delete the exported CSV, if there is one in the export location
        passwords_csv = os.path.join(downloads_dir, filename)
        if os.path.exists(passwords_csv):
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

    def _primary_password_prompt_present(self) -> bool:
        """Return True if a modal primary-password prompt is currently open."""
        try:
            self.driver.switch_to.alert
            return True
        except NoAlertPresentException:
            return False

    def _submit_export_primary_password(
        self, primary_password: str, attempts: int = 5
    ) -> BasePage:
        """
        Handle the modal 'Primary Password' prompt Firefox raises when exporting
        with a primary password set.

        Marionette cannot type into this prompt (it rejects Alert.send_keys), so
        the password is entered with OS-level keystrokes. The prompt also appears
        a moment after the export is confirmed, so wait for it before typing and
        re-enter until it dismisses (guards against typing before it is ready).
        """
        try:
            self.custom_wait(timeout=10).until(
                lambda _: self._primary_password_prompt_present()
            )
        except TimeoutException:
            logging.warning("No primary password prompt appeared during export.")
            return self

        for _ in range(attempts):
            if not self._primary_password_prompt_present():
                return self
            # Brief settle so the native prompt has keyboard focus before typing;
            # it is not in the DOM, so its readiness cannot be polled directly.
            sleep(self._NATIVE_PROMPT_SETTLE_S)
            self.gui.write(primary_password, interval=0.05)
            self.gui.press("enter")
            # Condition-based wait for the prompt to dismiss (instead of a fixed
            # sleep); only retry if it is still present afterward.
            try:
                self.custom_wait(timeout=5).until(
                    lambda _: not self._primary_password_prompt_present()
                )
                return self
            except TimeoutException:
                continue
        logging.warning(
            "Primary password export prompt was never dismissed after %d attempts.",
            attempts,
        )
        return self

    def export_passwords_csv(
        self,
        downloads_folder: str,
        filename: str,
        primary_password: Optional[str] = None,
    ) -> None:
        """
        Export passwords to a CSV file at the target location.

        The native "Save As" picker is mocked on all platforms so the export
        runs headlessly in CI (driving the OS file dialog is unreliable there).
        Disable the export re-auth prompt for logins that do not use a primary
        password by setting `signon.management.page.os-auth.locked.enabled` to
        False in the test's prefs.

        Args:
            downloads_folder (str): The folder where the CSV should be saved.
            filename (str): The name of the CSV file.
            primary_password (Optional[str]): If a primary password is set, the
                value to enter at the export re-authentication prompt.
        """
        target_path = os.path.join(downloads_folder, filename)
        self.install_mock_file_picker(target_path)

        # Open about:logins and click export buttons
        try:
            self.open()
            self.click_on("menu-button")
            self.click_on("export-passwords-button")
            self.click_on("continue-export-button")

            # A primary password (if set) must be re-entered before the save dialog.
            if primary_password:
                self._submit_export_primary_password(primary_password)

            self.wait_for_mock_file_picker()
        finally:
            self.cleanup_mock_file_picker()

    def click_copy_username_button(self) -> Page:
        """Click the copy username button"""
        self.click_on("copy-username")
        return self

    def click_copy_password_button(self) -> Page:
        """Click the copy password button"""
        self.click_on("copy-password")
        return self

    def click_reveal_password_button(self) -> Page:
        """Click the reveal password button"""
        self.click_on("show-password-checkbox")
        return self

    def verify_reveal_button_cursor_pointer(self):
        """
        Verify that hovering over the Reveal/Hide password button
        changes the mouse cursor to a hand pointer
        """
        element = self.get_element("show-password-checkbox")

        # hover over element
        ActionChains(self.driver).move_to_element(element).perform()

        # read computed cursor style
        cursor = element.value_of_css_property("cursor")

        assert cursor == "pointer", f"Expected pointer cursor, got {cursor}"

    @BasePage.context_chrome
    def enter_primary_password(self, primary_password, expected_tabs=2) -> BasePage:
        """
        Waits for the primary password prompt in chrome context,
        switches to the new tab, enters the password, and submits it.

        The prompt can reset its input field while it finishes initializing,
        which drops the typed password and leaves the dialog waiting. Re-enter
        the password until the value sticks, then submit, treating the prompt
        closing as success.
        """

        original_window = self.driver.current_window_handle

        # Wait until new tab (prompt) is opened
        self.wait_for_num_tabs(expected_tabs)

        # Switch to the newest tab
        self.driver.switch_to.window(self.driver.window_handles[-1])

        # Re-fetch element to avoid stale reference
        primary_password_prompt = self.get_element("primary-password-prompt")
        assert primary_password_prompt.is_displayed()

        enter_sent = False

        def _enter_and_submit(_):
            # wait_for_num_tabs(expected_tabs) already ran above, so if the count
            # has since dropped the dialog has closed — the definitive success
            # signal.
            nonlocal enter_sent
            if len(self.driver.window_handles) < expected_tabs:
                return True
            try:
                input_field = self.get_element("primary-password-dialog-input-field")
                # Re-enter if the dialog cleared the field during initialization;
                # allow ENTER again once the value has been re-typed.
                if input_field.get_attribute("value") != primary_password:
                    input_field.clear()
                    input_field.send_keys(primary_password)
                    enter_sent = False
                    return False
                # Send ENTER once per typed value; wait for closure on later polls
                # so it is not sent twice while the dialog is still processing.
                if not enter_sent:
                    input_field.send_keys(Keys.ENTER)
                    enter_sent = True
            except StaleElementReferenceException:
                # The dialog re-rendered mid-interaction; retry on the next poll.
                pass
            return False

        # Resolves once _enter_and_submit sees the prompt tab close.
        self.wait.until(_enter_and_submit)

        # Switch back after prompt closes
        self.driver.switch_to.window(original_window)

        return self

    @BasePage.context_chrome
    def dismiss_primary_password_prompt(self, expected_tabs=2) -> BasePage:
        """
        Switches to the primary password prompt tab and dismisses it using ESC.
        """

        original_window = self.driver.current_window_handle

        # Wait until new tab (prompt) is opened
        self.wait_for_num_tabs(expected_tabs)

        # Switch to the newest tab (prompt)
        self.driver.switch_to.window(self.driver.window_handles[-1])

        # Re-fetch element to avoid stale reference
        primary_password_prompt = self.get_element("primary-password-prompt")

        # Dismiss prompt
        primary_password_prompt.send_keys(Keys.ESCAPE)

        # Switch back after prompt closes
        self.wait.until(lambda d: len(d.window_handles) == 1)
        self.driver.switch_to.window(original_window)

        return self

    def assert_revealed_password(self, expected_password: str) -> BasePage:
        """Reveal saved password and assert it matches the expected value"""
        saved_password = self.get_element(
            "about-logins-page-password-revealed"
        ).get_attribute("value")

        assert saved_password == expected_password, (
            f"Expected '{expected_password}', got '{saved_password}'"
        )
        return self

    def dismiss_pp_if_appears(self, timeout=3):
        """
        Dismiss the Primary Password alert if it appears within timeout seconds
        """
        try:
            WebDriverWait(self.driver, timeout).until(EC.alert_is_present())
            self.driver.switch_to.alert.dismiss()
        except Exception:
            pass
        return self

    def enter_primary_password_native(self, primary_password, timeout=10) -> BasePage:
        """
        Unlock the login store by answering Firefox's native Primary Password prompt.

        Firefox 154 presents the Primary Password request for login-form autofill as
        a native tab-modal ``promptPassword`` dialog (not the older in-content page
        handled by :meth:`enter_primary_password`). Marionette rejects
        ``Alert.send_keys`` on it, so type via OS keystrokes and accept — the same
        approach used for the CSV-export re-auth prompt. Entering the correct
        password unlocks the store for the session, which stops it re-prompting on
        later reads (a cancel instead leaves it re-prompting persistently). Waits for
        the prompt, types, and waits for it to clear.
        """
        WebDriverWait(self.driver, timeout).until(EC.alert_is_present())
        # Brief settle so the native prompt has keyboard focus before typing; it is
        # not in the DOM, so its readiness cannot be polled directly.
        sleep(self._NATIVE_PROMPT_SETTLE_S)
        self.gui.write(primary_password, interval=0.05)
        self.gui.press("enter")
        WebDriverWait(self.driver, timeout).until_not(EC.alert_is_present())
        return self

    def assert_username_present(self, username: str) -> BasePage:
        """
        Waits until a visible login list item with the given username is present
        """
        self.wait.until(
            lambda _: any(
                r.get_attribute("username") == username
                for r in self.get_elements("login-list-item")
                if r.is_displayed()
            ),
            message=f"{username} not found in saved logins",
        )
        return self


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


class AboutProtections(BasePage):
    """
    POM for about:protections page
    """

    URL_TEMPLATE = "about:protections"

    def verify_lockwise_scanned_text(self, expected_count: int):
        """Verify the Lockwise 'N password(s) stored securely.' message matches `expected_count`."""
        expected = (
            f"{expected_count} password stored securely."
            if expected_count == 1
            else f"{expected_count} passwords stored securely."
        )
        self.element_has_text("lockwise-scanned-text", expected)
        return self

    def get_weekly_tracker_count(self) -> int:
        """Returns the number of trackers blocked over the past week from about:protections"""
        raw = self.get_attribute_value("graph-week-summary", "data-l10n-args")
        if not raw:
            return 0
        return json.loads(raw)["count"]


class AboutTelemetry(BasePage):
    """
    The POM for the about:telemetry page
    """

    URL_TEMPLATE = "about:telemetry"

    def open_raw_json_data(self):
        """
        Opens the Raw JSON telemetry view (against bnVsbA== / null payload timing).
        """
        existing_tabs = len(self.driver.window_handles)

        # Click "Raw JSON" from categories on the left
        self.element_clickable("category-raw")
        self.get_element("category-raw").click()

        # Wait for the new tab before switching
        self.wait.until(lambda d: len(d.window_handles) == existing_tabs + 1)
        self.switch_to_new_tab()
        self.clear_cache()

        # Wait for Raw Data tab to be clickable, then click it
        self.element_clickable("rawdata-tab")
        self.get_element("rawdata-tab").click()

        # Wait for data URL
        self.wait.until(
            lambda d: d.current_url.startswith("data:application/json;base64,")
        )

        # Wait until it's not the "null" payload (bnVsbA==); telemetry can take time to flush
        self.custom_wait(timeout=30).until(
            lambda d: "base64,bnVsbA==" not in d.current_url
        )

        return self

    def search_telemetry(self, term: str) -> "AboutTelemetry":
        search_box = self.get_element("search")
        search_box.clear()
        search_box.send_keys(term)
        return self

    def is_telemetry_entry_present(
        self, table_selector_key: str, expected_telemetry_data
    ) -> bool:
        """
        Generic method to check if a telemetry row exists in a given table.
        """

        # Wait for the table to exist in DOM
        self.get_element(table_selector_key)

        # Retrieve all rows from the telemetry table
        rows = self.get_elements(table_selector_key)

        for row in reversed(rows):
            cells = [cell.text.strip() for cell in row.find_elements(By.TAG_NAME, "td")]
            if all(value in cells for value in expected_telemetry_data):
                return True

        return False

    def is_telemetry_scalars_entry_present(self, expected_data):
        return self.is_telemetry_entry_present(
            "telemetry-scalars-table-rows", expected_data
        )

    def is_telemetry_events_entry_present(self, expected_data):
        return self.is_telemetry_entry_present(
            "telemetry-events-table-rows", expected_data
        )

    def is_telemetry_keyed_scalars_entry_present(self, expected_data):
        return self.is_telemetry_entry_present(
            "telemetry-keyed-scalars-table-rows", expected_data
        )

    # JS that reads a legacy keyed-scalar value directly from the Telemetry API.
    # Scraping the rendered about:telemetry table is unreliable across CI runners
    # because the page does not force a child-process flush; reading the snapshot
    # (after an explicit flush) mirrors the robust Glean BOM approach.
    _KEYED_SCALAR_JS = """
        const callback = arguments[arguments.length - 1];
        const wantedKey = arguments[0];
        (async () => {
            try {
                if (Services.fog && Services.fog.testFlushAllChildren) {
                    await Services.fog.testFlushAllChildren();
                }
                const snapshot =
                    Services.telemetry.getSnapshotForKeyedScalars("main", false) || {};
                let value = null;
                for (const proc of Object.keys(snapshot)) {
                    const scalars = snapshot[proc] || {};
                    for (const name of Object.keys(scalars)) {
                        const keyed = scalars[name] || {};
                        if (Object.prototype.hasOwnProperty.call(keyed, wantedKey)) {
                            value = keyed[wantedKey];
                        }
                    }
                }
                callback(value);
            } catch (e) {
                callback({ error: String(e) });
            }
        })();
    """

    @BasePage.context_chrome
    def poll_keyed_scalar(
        self,
        key: str,
        expected_value,
        timeout: int = 30,
        poll_interval: float = 0.5,
    ) -> bool:
        """Poll a legacy keyed scalar until `key` reaches `expected_value`.

        Reads the scalar snapshot directly via the chrome Telemetry API rather
        than scraping about:telemetry, forcing a flush first. Returns True on
        match, False on timeout.
        """
        end_time = time() + timeout
        last = None
        while time() < end_time:
            result = self.driver.execute_async_script(self._KEYED_SCALAR_JS, key)
            if isinstance(result, dict) and "error" in result:
                raise AssertionError(f"Telemetry JS error: {result['error']}")
            last = result
            if result is not None and str(result) == str(expected_value):
                return True
            sleep(poll_interval)
        logging.warning(
            "Keyed scalar %r did not reach %r within %ss (last=%r)",
            key,
            expected_value,
            timeout,
            last,
        )
        return False


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

    def get_all_dns_rows(self) -> list[tuple[str, str]]:
        """Get all DNS rows as (host, trr) text tuples.

        Caller must ensure the DNS table is visible before calling. Returns []
        if an individual row goes stale mid-iteration (table is re-rendering);
        callers that poll can treat [] as a retry signal.
        """
        rows = self.find_elements(By.XPATH, "//tbody[@id='dns_content']/tr")
        result = []
        for row in rows:
            try:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) >= 3:
                    result.append(
                        (cells[0].text.strip(), cells[2].text.strip().lower())
                    )
            except StaleElementReferenceException:
                continue
        return result

    def wait_for_dns_entry(self, host: str, trr: str = "true") -> BasePage:
        """Wait until a DNS entry for the given host appears in the table.

        Ensures the table is visible before polling.
        """
        self.element_visible("dns-content")

        expected_host = host.strip()
        expected_trr = trr.strip().lower()

        def _entry_present(_):
            return any(
                row_host == expected_host and row_trr == expected_trr
                for row_host, row_trr in self.get_all_dns_rows()
            )

        self.custom_wait(timeout=30).until(
            _entry_present,
            message=f"DNS entry for host '{host}' with TRR='{trr}' did not appear",
        )
        return self


class AboutGlean(BasePage):
    """POM for about:glean"""

    URL_TEMPLATE = "about:glean"

    def change_ping_id(self, ping_id: str) -> "AboutGlean":
        """Change the Glean ping id to the given string."""
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
