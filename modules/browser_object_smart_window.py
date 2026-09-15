import logging

from selenium.webdriver.common.keys import Keys

from modules.page_base import BasePage

AI_WINDOW_MODULE = "moz-src:///browser/components/aiwindow/ui/modules/AIWindow.sys.mjs"


class SmartWindow(BasePage):
    """
    Browser Object Model for the Smart Window (AI Window) chrome.

    Covers the Switch Windows button and its Classic/Smart panel, plus the
    chrome that only exists while a window is in the Smart Window state.
    """

    URL_TEMPLATE = "about:blank"

    # ── Smart Window state ───────────────────────────────────────────────

    @BasePage.context_chrome
    def is_smart_window_active(self) -> bool:
        """
        Report whether the current window is in the Smart Window state.

        Reads AIWindow.isAIWindowActive rather than the `ai-window` attribute
        so the check follows the product's own definition of "active".
        """
        return self.driver.execute_script(
            f"""
            const {{ AIWindow }} = ChromeUtils.importESModule("{AI_WINDOW_MODULE}");
            return AIWindow.isAIWindowActive(window);
            """
        )

    def expect_smart_window_active(self, active: bool = True) -> BasePage:
        """
        Wait until the current window is (or is not) a Smart Window.
        """
        self.expect(lambda _: self.is_smart_window_active() == active)
        return self

    def activate_smart_window(self) -> BasePage:
        """
        Put the current window into the Smart Window state (test harness only,
        bypasses the FxA sign-in gate). Do not use where the entry point itself
        is under test -- assert the sign-in redirect (see C3248785).
        """
        logging.info("Activating Smart Window state via AIWindow.toggleAIWindow")
        # Scope chrome to just the execute_script; expect_smart_window_active
        # handles its own context via self.expect (@context_of_model).
        with self.driver.context(self.driver.CONTEXT_CHROME):
            # Call AIWindow.toggleAIWindow directly: same call the product makes
            # after auth, without routing through AIWindowAccountAuth.
            self.driver.execute_script(
                f"""
                const {{ AIWindow }} = ChromeUtils.importESModule("{AI_WINDOW_MODULE}");
                AIWindow.toggleAIWindow(window, true, "other");
                """
            )
        self.expect_smart_window_active(True)
        return self

    # ── Switch Windows button ────────────────────────────────────────────

    def open_window_switcher(self) -> BasePage:
        """
        Click the Switch Windows button and wait for its panel to open.
        """
        self.click_on("window-switcher-button")
        self.element_visible("window-switcher-view")
        return self

    @BasePage.context_chrome
    def close_window_switcher(self) -> BasePage:
        """
        Dismiss the Switch Windows panel with ESC.
        """
        self.actions.send_keys(Keys.ESCAPE).perform()
        self.element_not_visible("window-switcher-view")
        return self

    @BasePage.context_of_model
    def get_switcher_selection(self) -> str:
        """
        Return which entry the Switch Windows panel shows as current.

        Returns
        -------
        str
            "smart", "classic", or "none" if neither is checked.
        """
        for name, label in (
            ("switch-to-smart", "smart"),
            ("switch-to-classic", "classic"),
        ):
            # The panel sets state with toggleAttribute, so an unselected entry
            # has no attribute at all. Reject "false" anyway, so a future
            # checked="false" would not read as selected.
            checked = self.get_element(name).get_attribute("checked")
            if checked and checked != "false":
                return label
        return "none"

    def expect_switcher_selection(self, expected: str) -> BasePage:
        """
        Wait until the Switch Windows panel marks `expected` as current.
        """
        self.expect(lambda _: self.get_switcher_selection() == expected)
        return self

    def switch_to_classic_window(self) -> BasePage:
        """
        Switch the current window to a Classic Window via the Switch Windows
        button, and wait for the switch to take effect.
        """
        self.open_window_switcher()
        self.click_on("switch-to-classic")
        self.expect_smart_window_active(False)
        return self

    def click_switch_to_smart_window(self) -> BasePage:
        """
        Click the Smart entry in the Switch Windows panel.

        Does not wait for a Smart Window: while signed out this navigates to
        the FxA sign-in page instead.
        """
        self.open_window_switcher()
        self.click_on("switch-to-smart")
        return self

    # ── Tabs ─────────────────────────────────────────────────────────────

    @BasePage.context_chrome
    def get_selected_tab_url(self) -> str:
        """
        Return the URL of the selected tab, read from chrome.

        Used instead of driver.current_url where the action under test opens a
        new tab, since the content-context handle can still point at the old
        one.
        """
        return self.driver.execute_script(
            "return gBrowser.selectedBrowser.currentURI.spec;"
        )

    def expect_selected_tab_url_contains(self, fragment: str) -> BasePage:
        """
        Wait until the selected tab's URL contains `fragment`.
        """
        self.expect(lambda _: fragment in self.get_selected_tab_url())
        return self
