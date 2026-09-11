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

    @BasePage.context_chrome
    def activate_smart_window(self) -> BasePage:
        """
        Put the current window into the Smart Window state.

        TEST HARNESS ONLY. This calls AIWindow.toggleAIWindow directly, which
        is the same call the product makes *after* it has authorized the user.
        Going through the UI instead (the Switch Windows button, the hamburger
        menu, the AI settings link) routes through
        AIWindowAccountAuth.ensureAIWindowAccess, which needs a live FxA
        account and so cannot run in this suite.

        Use this to reach Smart Window surfaces whose *behaviour* is under
        test. Do not use it in a test whose subject is the entry point itself
        -- assert the sign-in redirect instead (see C3248785).
        """
        logging.info("Activating Smart Window state via AIWindow.toggleAIWindow")
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

    @BasePage.context_chrome
    def switcher_button_available(self) -> bool:
        """
        Report whether the Switch Windows button is offered in this window.

        Checks visibility, not merely existence. The three ways Smart Window
        can be unavailable do not look alike in the DOM:

        - Private Browsing window -> the widget is never built (no element)
        - browser.smartwindow.enabled=false -> element exists with hidden=true
        - blocked in AI Controls -> the widget is destroyed (no element)

        An existence-only check would call the middle case "available", which
        would let a test pass with the feature switched off.

        Drops the implicit wait so an absent button returns immediately rather
        than costing a full timeout.
        """
        original = self.driver.timeouts.implicit_wait
        self.driver.implicitly_wait(0)
        try:
            elements = self.get_elements("window-switcher-button")
            return bool(elements) and elements[0].is_displayed()
        finally:
            self.driver.implicitly_wait(original)

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

    # ── Windows ──────────────────────────────────────────────────────────

    def wait_for_new_window(self, known_handles: set[str]) -> str:
        """
        Wait for a window outside `known_handles` to open, and return its handle.

        Deliberately waits with self.wait rather than self.expect: expect is
        wrapped in context_of_model, and window_handles is context-sensitive --
        chrome context lists browser windows, content context lists tabs.
        Diffing a chrome-context list against a content-context baseline
        returns a handle for the wrong window, so this stays in whichever
        context the caller captured `known_handles` in.

        Arguments
        ---------
        known_handles: set[str]
            driver.window_handles captured before the action that opens a window.
        """
        opened: set[str] = set()

        def _new_window(driver) -> bool:
            nonlocal opened
            opened = set(driver.window_handles) - known_handles
            return bool(opened)

        self.wait.until(_new_window)
        return opened.pop()
