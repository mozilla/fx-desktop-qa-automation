from typing import Literal

from modules.page_base import BasePage

Reason = Literal[
    "account",
    "adblocker",
    "checkout",
    "content",
    "deceptive",
    "load",
    "media",
    "notsupported",
    "other",
    "slow",
]


class ReportBrokenSite(BasePage):
    """
    BOM for the Report Broken Site panel
    """

    URL_TEMPLATE = ""

    @BasePage.context_chrome
    def select_reason(self, reason: Reason) -> BasePage:
        """
        Pick a reason from the "What's broken" section, which opens the details view.
        """
        self.element_clickable("report-broken-site-reason", labels=[reason])
        # A click that lands while the panel is still sliding in gets dropped.
        self.element_does_not_have_attribute("panel-multi-view", "transitioning")
        self.js_click_on("report-broken-site-reason", labels=[reason])
        self.element_visible("report-broken-site-details-view")
        return self

    @BasePage.context_chrome
    def fill_description(self, description: str) -> BasePage:
        """Write into the description textarea of the details view."""
        # The textarea is not interactable until the details view has finished sliding in.
        self.element_does_not_have_attribute("panel-multi-view", "transitioning")
        self.element_clickable("report-broken-site-description")
        self.fill(
            "report-broken-site-description",
            description,
            clear_first=False,
            press_enter=False,
        )
        return self

    @BasePage.context_chrome
    def send_report(self) -> BasePage:
        """Click the Send Report button."""
        self.element_clickable("report-broken-site-send-button")
        self.js_click_on("report-broken-site-send-button")
        return self

    @BasePage.context_chrome
    def report_sent_confirmation_displayed(self) -> BasePage:
        """Verify the details view is replaced by the confirmation view."""
        self.element_visible("report-broken-site-sent-view")
        self.element_visible("report-broken-site-sent-message")
        self.element_not_visible("report-broken-site-details-view")
        return self

    @BasePage.context_chrome
    def click_okay(self) -> BasePage:
        """Dismiss the confirmation view with the "Okay" button."""
        self.element_clickable("report-broken-site-okay-button")
        self.js_click_on("report-broken-site-okay-button")
        return self

    @BasePage.context_chrome
    def panel_is_dismissed(self) -> BasePage:
        """Verify the Report Broken Site panel is no longer showing."""
        self.element_not_visible("report-broken-site-sent-view")
        self.element_not_visible("report-broken-site-main-view")
        return self
