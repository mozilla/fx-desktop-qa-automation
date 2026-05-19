import json
import logging
from time import sleep

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from modules.browser_object_navigation import Navigation
from modules.page_base import BasePage


class TrustPanel(BasePage):
    """
    BOM for the panel that shows up after clicking the shield
    """

    URL_TEMPLATE = ""

    @BasePage.context_chrome
    def open_panel(self) -> BasePage:
        self.click_on("shield-icon")
        return self

    @BasePage.context_chrome
    def item_in_block(self, item: str, block: WebElement) -> bool:
        intext = block.text.endswith(item) or block.text.endswith(f"{item}s")
        inattr = block.get_attribute("data-l10n-id").endswith(item)
        return intext or inattr

    @BasePage.context_chrome
    def trackers_in_category(self, category: str, *trackers) -> bool:
        """Confirm that text or data-l10n-id for blocked items exists within blocked area"""
        sleep(0.5)  # Must hard-wait because trackers may not exist
        spotted = self.get_elements(f"{category}-items")
        if trackers and not spotted:
            return False
        for tracker in trackers:
            if not any([self.item_in_block(tracker, block) for block in spotted]):
                return False
        return True

    @BasePage.context_chrome
    def trackers_blocked(self, *trackers) -> bool:
        assert self.trackers_in_category("blocked", *trackers), (
            f"Trackers {trackers} not blocked"
        )

    @BasePage.context_chrome
    def trackers_detected(self, *trackers) -> bool:
        assert self.trackers_in_category("detected", *trackers), (
            f"Trackers {trackers} not detected"
        )

    @BasePage.context_chrome
    def get_element_args(self, reference: str | tuple | WebElement, labels=None):
        raw_args = self.fetch(reference, labels).get_attribute("data-l10n-args")
        return json.loads(raw_args)

    @BasePage.context_chrome
    def assert_no_trackers(self) -> bool:
        args = self.get_element_args("trustpanel-blocker-section")
        assert args.get("count") == 0

    @BasePage.context_chrome
    def sites_in_category(self, category, *sites) -> bool:
        def _inval(element: WebElement, val):
            return element.get_attribute("value").endswith(val)

        spotted = self.get_elements(f"{category}-site-entry")
        if sites and not spotted:
            return False
        for site in sites:
            if not any([_inval(entry, site) for entry in spotted]):
                return False
        return True

    @BasePage.context_chrome
    def sites_blocked(self, *sites) -> bool:
        return self.sites_in_category("blocked", *sites)

    @BasePage.context_chrome
    def sites_detected(self, *sites) -> bool:
        return self.sites_in_category("detected", *sites)

    @BasePage.context_chrome
    def wait_for_trackers(self) -> BasePage:
        """Open and close the trust panel until trackers appear"""
        nav = Navigation(self.driver)
        blocker_section = "trustpanel-blocker-section"

        def _check_trustpanel(driver):
            args = self.get_element_args(blocker_section)
            if args.get("count"):
                return True

            nav.click_on("refresh-button")

            self.open_panel()
            if self.get_parent_of(blocker_section).get_attribute("hidden") == "true":
                return False
            return True

        self.expect(_check_trustpanel)

    @BasePage.context_chrome
    def assert_connection_information(self, expected_technical_details):
        self.element_clickable("trustpanel-connect-button")
        self.click_on("trustpanel-connect-button")
        link = self.fetch("trustpanel-connect-details-link")
        self.driver.execute_script("arguments[0].click()", link)
        self.driver.switch_to.window(self.driver.window_handles[-1])

        technical_details = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "security-technical-shortform"))
        )
        sleep(0.5)
        assert technical_details.get_attribute("value") == expected_technical_details, (
            f"Expected '{expected_technical_details}' but found "
            f"'{technical_details.get_attribute('value')}'"
        )

    @BasePage.context_chrome
    def click_see_all(self) -> BasePage:
        """Clicks the "See All" button in the trackers panel"""
        self.js_click_on("see-all-trackers")
        return self

    @BasePage.context_chrome
    def has_detected_tracking_sites(self, *expected_sites) -> bool:
        """Checks whether the expected tracking domains are detected in the protections popup."""
        elements = self.get_elements("protections-popup-list-host-label")

        if expected_sites and not elements:
            return False

        # Extract the "value" attribute from each label element
        values = [el.get_attribute("value") for el in elements if el]

        for site in expected_sites:
            if not any(val and val.endswith(site) for val in values):
                return False

        return True

    @BasePage.context_chrome
    def not_blocked_trackers_title_displayed_in_subpanel(self, category: str):
        """
        Verify that the 'Not Blocking <Category>' title
        is displayed in the subpanel.
        """
        self.element_visible("not-blocking-category", labels=[category.title()])
        return self

    @BasePage.context_chrome
    def open_detected_category(self, category: str):
        """
        Open a detected tracker category from the protections panel.

        Canonical input format: hyphenated singular (e.g. "tracking-content")
        """
        canonical = category.strip().lower().replace(" ", "-")
        locator = (
            "detected-category",
            [f"trustpanel-list-label-{canonical}"],
        )

        sleep(0.5)
        self.js_click_on(*locator)
        return self

    @BasePage.context_chrome
    def blocked_trackers_title_displayed_in_subpanel(self, category: str):
        """Verify that the subpanel title for the blocked tracker category is visible."""
        self.element_visible("blocked-trackers-title", labels=[category.title()])
        return self

    @BasePage.context_chrome
    def trustpanel_toggle_on_off(self):
        """Trust panel toggle button"""
        self.js_click_on("trustpanel-toggle-button")
        return self

    @BasePage.context_chrome
    def trustpanel_status(self, status: str):
        """
        Verify Trust Panel ETP status.
        status: "on" | "off"
        """

        mapping = {
            "on": "trustpanel-etp-on",
            "off": "trustpanel-etp-off",
        }

        if status not in mapping:
            raise ValueError("status must be 'on' or 'off'")

        self.element_visible(mapping[status])
        return self

    @BasePage.context_chrome
    def click_tracking_protection_toggle(self):
        """Clicks the "Enhanced Tracking Protection" toggle in the trackers panel"""
        self.js_click_on("trustpanel-toggle-button")
        return self
