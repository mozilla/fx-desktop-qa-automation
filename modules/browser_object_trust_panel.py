import json
from time import sleep

from selenium.common import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
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
        """
        Ensure the trust panel is open.

        Clicking the shield icon toggles the panel, so we only click when it is
        not already open. This keeps the method idempotent and safe to call from
        retry/fallback paths without accidentally toggling an open panel closed.
        """
        if not self._panel_is_open():
            self.element_clickable("shield-icon")
            self.click_on("shield-icon")
        self.element_visible("trustpanel")
        return self

    def _panel_is_open(self) -> bool:
        """Return True when the trust panel popup is open or opening."""
        original = self.driver.timeouts.implicit_wait
        self.driver.implicitly_wait(0)

        try:
            return any(
                panel.get_attribute("state") in ("open", "showing")
                for panel in self.get_elements("trustpanel")
            )
        except StaleElementReferenceException:
            return False
        finally:
            self.driver.implicitly_wait(original)

    @BasePage.context_chrome
    def item_in_block(self, item: str, block: WebElement) -> bool:
        text = block.text or ""
        l10n_id = block.get_attribute("data-l10n-id") or ""
        intext = text.endswith(item) or text.endswith(f"{item}s")
        inattr = l10n_id.endswith(item)
        return intext or inattr

    @BasePage.context_chrome
    def trackers_in_category(self, category: str, *trackers) -> BasePage:
        """Wait until the expected trackers appear in the requested category."""

        def _expected_trackers_are_present(_):
            try:
                spotted = self.get_elements(f"{category}-items")

                if trackers and not spotted:
                    return False

                return all(
                    any(self.item_in_block(tracker, block) for block in spotted)
                    for tracker in trackers
                )
            except StaleElementReferenceException:
                return False

        try:
            self.expect(_expected_trackers_are_present)
        except TimeoutException as exc:
            raise AssertionError(
                f"Trackers {trackers} were not found in the '{category}' category."
            ) from exc

        return self

    @BasePage.context_chrome
    def trackers_blocked(self, *trackers) -> BasePage:
        """Wait until the expected trackers appear in the blocked category."""
        return self.trackers_in_category("blocked", *trackers)

    @BasePage.context_chrome
    def trackers_detected(self, *trackers) -> BasePage:
        """Wait until the expected trackers appear in the detected category."""
        return self.trackers_in_category("detected", *trackers)

    @BasePage.context_chrome
    def get_element_args(self, reference: str | tuple | WebElement, labels=None):
        raw_args = self.fetch(reference, labels).get_attribute("data-l10n-args")
        return json.loads(raw_args)

    @BasePage.context_chrome
    def assert_no_trackers(self) -> None:
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
    def wait_for_trackers(
            self,
            expect_blocked: bool = True,
            attempts: int = 3,
            timeout: int = 10,
    ) -> BasePage:
        """
        Wait until the trust panel has finished populating.

        With ``expect_blocked`` True (the default, for pages that block
        trackers) wait for the blocked-tracker count to become positive,
        reloading and reopening the panel between attempts. Waiting for the
        count avoids the race where the panel is visible before the blocked
        count has populated; AssertionError is raised if no blocked trackers
        ever appear.

        With ``expect_blocked`` False (ETP disabled, or the category under test
        is allowed) the blocked count stays 0, so instead wait only for the
        blocker section to render -- count 0 is a valid populated state -- and
        return without reloading the page (which would discard any subview the
        caller has navigated into). AssertionError is raised if the section
        never renders.
        """
        if attempts < 1:
            raise ValueError("attempts must be at least 1")

        if not expect_blocked:
            self.open_panel()
            try:
                self.custom_wait(timeout=timeout).until(
                    lambda _: self._blocked_tracker_count() is not None
                )
            except TimeoutException as exc:
                raise AssertionError(
                    "Trust panel blocker section did not render."
                ) from exc
            return self

        nav = Navigation(self.driver)
        for attempt in range(1, attempts + 1):
            self.open_panel()
            try:
                self.custom_wait(timeout=timeout).until(
                    lambda _: (self._blocked_tracker_count() or 0) > 0
                )
                return self
            except TimeoutException:
                if attempt < attempts:
                    nav.refresh_page()

        raise AssertionError(
            f"No blocked trackers appeared in the trust panel after {attempts} attempts."
        )

    def _blocked_tracker_count(self) -> int | None:
        """
        Return the blocked-tracker count from the panel header.

        Returns None when the blocker section has not rendered or its
        localization args cannot be parsed yet.
        """
        original = self.driver.timeouts.implicit_wait
        self.driver.implicitly_wait(0)
        try:
            args = self.get_element_args("trustpanel-blocker-section")
        except (
                NoSuchElementException,
                StaleElementReferenceException,
                TypeError,
                ValueError,
        ):
            return None
        finally:
            self.driver.implicitly_wait(original)
        if not isinstance(args, dict):
            return None
        return args.get("count", 0)

    def _wait_for_panel_button(
            self,
            reference: str,
            labels: list[str] | None = None,
    ) -> WebElement:
        """Wait for an enabled button in the visible panel view."""

        def _button_is_ready(_):
            try:
                for button in self.get_elements(reference, labels=labels):
                    if not button.is_displayed() or not button.is_enabled():
                        continue

                    panel_is_ready = self.driver.execute_script(
                        """
                        const button = arguments[0];
                        const view = button.closest("panelview");
                        const multiview = button.closest("panelmultiview");

                        return Boolean(
                            view?.hasAttribute("visible") &&
                            multiview &&
                            !multiview.hasAttribute("transitioning")
                        );
                        """,
                        button,
                    )

                    if panel_is_ready:
                        return button

            except StaleElementReferenceException:
                return False

            return False

        return self.wait.until(_button_is_ready)

    def _wait_for_panel_view(self, *, main_view: bool) -> None:
        """Wait until panel navigation finishes on the requested view type."""

        self.wait.until(
            lambda _: self.driver.execute_script(
                """
                const popup = document.getElementById("trustpanel-popup");
                const multiview = popup?.querySelector("panelmultiview");
                const visibleView =
                    multiview?.querySelector("panelview[visible]");

                if (
                    !multiview ||
                    !visibleView ||
                    multiview.hasAttribute("transitioning")
                ) {
                    return false;
                }

                return (
                    visibleView.hasAttribute("mainview") === arguments[0]
                );
                """,
                main_view,
            )
        )

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
    def open_detected_category(self, category: str) -> BasePage:
        """
        Open a detected tracker category from the protections panel.

        Canonical input format: hyphenated singular
        (e.g. "tracking-content").
        """
        canonical = category.strip().lower().replace(" ", "-")

        button = self._wait_for_panel_button(
            "detected-category",
            labels=[f"trustpanel-list-label-{canonical}"],
        )

        self.driver.execute_script("arguments[0].click();", button)
        self._wait_for_panel_view(main_view=False)

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
    def click_connection_button(self):
        """Click the connection section button from the Trust Panel."""
        self.element_visible("trustpanel-connection-button")
        self.click_on("trustpanel-connection-button")
        # Wait for the subview to actually render
        try:
            self.element_visible("connection-subview")
        except TimeoutException:
            # Retry click
            self.click_on("trustpanel-connection-button")
        return self

    @BasePage.context_chrome
    def connection_not_secure_message_displayed(self):
        """
        Verify the 'You are not securely connected to this site.'
        message is displayed in the connection subpanel.
        """
        self.element_visible("connection-not-secure")
        return self

    @BasePage.context_chrome
    def connection_secure_message_displayed(self):
        """
        Verify the 'You are securely connected to this site.'
        message is displayed in the connection subpanel.
        """
        self.element_visible("connection-secure")
        return self

    @BasePage.context_chrome
    def click_privacy_settings_link(self):
        """Click the 'Privacy Settings' footer link in the Trust Panel."""
        self.element_visible("trustpanel-privacy-link")
        self.js_click_on("trustpanel-privacy-link")
        return self

    @BasePage.context_chrome
    def clear_cookies_site_data_via_panel(self):
        """Clear cookies and site data for the current site via the Trust Panel."""
        self.js_click_on("clear-cookies-button")
        self.js_click_on("clear-button")
        return self

    @BasePage.context_chrome
    def panel_is_dismissed(self):
        """Verify the Trust Panel is closed via its state attribute."""
        panel = self.get_element("trustpanel")
        self.expect(lambda _: panel.get_attribute("state") == "closed")
        return self

    @BasePage.context_chrome
    def click_subview_back_button(self) -> BasePage:
        """Return from the current subview to the main Trust Panel."""

        button = self._wait_for_panel_button("trustpanel-subview-back-button")

        self.driver.execute_script("arguments[0].click();", button)
        self._wait_for_panel_view(main_view=True)

        return self

    @BasePage.context_chrome
    def get_tracker_count(self) -> int:
        """Returns the total tracker count displayed in the main panel"""
        return self.get_element_args("trustpanel-blocker-section").get("count")

    @BasePage.context_chrome
    def get_cross_site_cookies_count(self) -> int:
        """Returns the cross-site tracking cookies count, 0 if not present"""
        try:
            return int(
                self.get_element_args("trustpanel-cross-site-cookies-count").get(
                    "count"
                )
            )
        except (TypeError, NoSuchElementException):
            return 0

    @BasePage.context_chrome
    def get_fingerprinter_count(self) -> int:
        """Returns the fingerprinter count, 0 if not present"""
        try:
            return int(
                self.get_element_args("trustpanel-fingerprinter-count").get("count")
            )
        except (TypeError, NoSuchElementException):
            return 0
