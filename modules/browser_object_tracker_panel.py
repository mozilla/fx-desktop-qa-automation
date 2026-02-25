import logging
from typing import List, Optional, Set

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webelement import WebElement

from modules.browser_object_navigation import Navigation
from modules.page_base import BasePage


class TrackerPanel(BasePage):
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
        return block.text.endswith(item) or block.get_attribute(
            "data-l10n-id"
        ).endswith(item)

    @BasePage.context_chrome
    def trackers_in_category(self, category: str, *trackers) -> bool:
        """Confirm that text or data-l10n-id for blocked items exists within blocked area"""
        blocked = self.get_elements(f"{category}-items")
        if trackers and not blocked:
            return False
        for tracker in trackers:
            if not any([self.item_in_block(tracker, b) for b in blocked]):
                return False
        return True

    @BasePage.context_chrome
    def trackers_blocked(self, *trackers) -> bool:
        return self.trackers_in_category("blocked", *trackers)

    @BasePage.context_chrome
    def trackers_detected(self, *trackers) -> bool:
        return self.trackers_in_category("detected", *trackers)

    @BasePage.context_chrome
    def verify_tracker_panel_title(self, expected_title):
        """
        verify the title of the tracker panel.
        """
        self.expect(
            lambda _: (
                self.get_element("tracker-title").get_attribute("innerHTML")
                == "Protections for senglehardt.com"
            )
        )

    def wait_for_blocked_tracking_icon(
        self, nav: Navigation, page: BasePage
    ) -> BasePage:
        """
        Waits for the shield icon to indicate that cookies/trackers are being blocked by continuously refreshing the page

        Remember to open the passed in page beforehand, this waits for the page to load.

        Example Usage:
        first_tracker_website.open()
        tracker_panel.wait_for_blocked_tracking_icon(nav, first_tracker_website)
        """

        def shield_active() -> bool:
            nav.get_element("refresh-button").click()
            with self.driver.context(self.driver.CONTEXT_CONTENT):
                page.open()
                page.wait_for_page_to_load()
            shield_icon = self.get_element("shield-icon")
            if (
                shield_icon.get_attribute("data-l10n-id")
                == "tracking-protection-icon-active-container"
            ):
                return True
            return False

        try:
            with self.driver.context(self.context_id):
                self.wait.until(lambda _: shield_active())
        except TimeoutException:
            logging.warning(
                "Shield icon not active after refreshing multiple times, the test has timed out."
            )
        return self

    def wait_for_trackers(self, nav: Navigation, page: BasePage) -> BasePage:
        """
        Waits for trackers to appear

        Remember to open the passed in page beforehand, this waits for the page to load.

        Example Usage:
        first_tracker_website.open()
        tracker_panel.wait_for_blocked_tracking_icon(nav, first_tracker_website)
        """

        def message_not_present() -> bool:
            nav.get_element("refresh-button").click()
            with self.driver.context(self.driver.CONTEXT_CONTENT):
                page.open()
                page.wait_for_page_to_load()
            self.get_element("shield-icon").click()
            no_trackers_message = self.get_element("no-trackers-message")
            if no_trackers_message.get_attribute("hidden") == "true":
                return True
            return False

        try:
            with self.driver.context(self.context_id):
                self.wait.until(lambda _: message_not_present())
        except TimeoutException:
            logging.warning("No trackers were ever detected after the timeout period.")
        return self

    def verify_tracker_shield_indicator(self, nav: Navigation) -> BasePage:
        """
        Verifies that the shield icon is in the correct mode
        """
        with self.driver.context(self.context_id):
            shield_icon = self.get_element("shield-icon")
            assert (
                shield_icon.get_attribute("data-l10n-id")
                == "tracking-protection-icon-active-container"
            ), (
                "The label detected did not correspond to the expected one: tracking-protection-icon-active-container"
            )
        return self

    @BasePage.context_chrome
    def open_and_return_cross_site_trackers(self) -> List[str]:
        self.get_element("tracker-cross-site-tracking").click()
        return [
            val.get_attribute("value")
            for val in self.get_elements("tracking-cross-site-tracking-item")
        ]

    @BasePage.context_chrome
    def open_and_return_allowed_trackers(self) -> List[str]:
        self.get_element("tracker-tracking-content").click()
        return [
            val.get_attribute("value")
            for val in self.get_elements("tracking-allowed-content-item")
        ]
