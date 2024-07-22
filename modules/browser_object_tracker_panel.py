from modules.browser_object_navigation import Navigation
from modules.page_base import BasePage


class TrackerPanel(BasePage):
    """
    BOM for the panel that shows up after clicking the shield
    """

    URL_TEMPLATE = ""
    NAV = None

    def wait_for_blocked_tracking_icon(self, nav: Navigation, page: BasePage):
        """
        Waits for the shield icon to indicate that cookies/trackers are being blocked by continuously refresing the page
        """
        self.driver.set_context(self.driver.CONTEXT_CHROME)

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
