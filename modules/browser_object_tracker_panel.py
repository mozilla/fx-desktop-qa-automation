from typing import List

from selenium.webdriver.remote.webelement import WebElement

from modules.browser_object_navigation import Navigation
from modules.page_base import BasePage


class TrackerPanel(BasePage):
    """
    BOM for the panel that shows up after clicking the shield
    """

    URL_TEMPLATE = ""

    def wait_for_blocked_tracking_icon(
        self, nav: Navigation, page: BasePage
    ) -> BasePage:
        """
        Waits for the shield icon to indicate that cookies/trackers are being blocked by continuously refresing the page

        Remember to open the passed in page beforehand, this waits for the page to load.

        Example Usage:
        first_tracker_website.open()
        tracker_panel.wait_for_blocked_tracking_icon(nav, first_tracker_website)
        """
        self.driver.set_context(self.driver.CONTEXT_CHROME)
        try:
            while 1:
                nav.get_element("refresh-button").click()

                self.driver.set_context(self.driver.CONTEXT_CONTENT)
                page.wait_for_page_to_load()

                self.driver.set_context(self.driver.CONTEXT_CHROME)
                shield_icon = nav.get_element("shield-icon")

                if (
                    shield_icon.get_attribute("data-l10n-id")
                    == "tracking-protection-icon-active-container"
                ):
                    return
        finally:
            self.driver.set_context(self.driver.CONTEXT_CONTENT)
        return self

    def verify_tracker_shield_indicator(self, nav: Navigation) -> BasePage:
        with self.driver.context(self.driver.CONTEXT_CHROME):
            shield_icon = nav.get_element("shield-icon")
            assert (
                shield_icon.get_attribute("data-l10n-id")
                == "tracking-protection-icon-active-container"
            ), "The label detected did not correspond to the expected one: tracking-protection-icon-no-trackers-detected-container"

    def open_and_return_cross_site_trackers(self) -> List[WebElement]:
        self.get_element("tracker-cross-site-tracking").click()
        return self.get_elements("tracking-cross-site-tracking-item")

    def open_and_return_allowed_trackers(self) -> List[WebElement]:
        self.get_element("tracker-tracking-content").click()
        return self.get_elements("tracking-allowed-content-item")
