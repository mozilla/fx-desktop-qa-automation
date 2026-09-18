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

    # ── AI chat sidebar ──────────────────────────────────────────────────

    @BasePage.context_of_model
    def ai_sidebar_open(self) -> bool:
        """
        Report whether the AI chat sidebar is open.

        Measures rendered geometry rather than the `hidden` attribute: the
        container is present but collapsed before the sidebar has ever been
        opened, and collapses again on close, without `hidden` ever changing.
        """
        rect = self.get_element("smart-window-box").rect
        return rect["width"] > 0 and rect["height"] > 0

    def expect_ai_sidebar_open(self, is_open: bool = True) -> BasePage:
        """Wait until the AI chat sidebar is (or is not) open."""
        self.expect(lambda _: self.ai_sidebar_open() == is_open)
        return self

    def toggle_ai_sidebar(self) -> BasePage:
        """
        Click the Ask button, which opens the sidebar when closed and closes
        it when open.
        """
        self.click_on("smart-window-ask-button")
        return self

    def close_ai_sidebar(self) -> BasePage:
        """
        Close the AI chat sidebar with its own X button.

        The button lives inside <browser id="ai-window-browser">, several
        shadow roots down, which the components.json selector system cannot
        traverse, so the walk runs in privileged JS. Matched on its
        data-l10n-id so the lookup does not depend on the UI locale.
        """

        # The container becomes visible before the document inside
        # ai-window-browser finishes loading, and a click landing during that
        # window is dropped. Poll on the outcome -- clicking again each time
        # the sidebar is still open -- rather than clicking once and hoping.
        # The X is close-only, not a toggle, so a repeat click cannot reopen.
        def _closed(_) -> bool:
            if not self.ai_sidebar_open():
                return True
            self._click_sidebar_close_button()
            return False

        self.expect(_closed)
        return self

    @BasePage.context_chrome
    def _click_sidebar_close_button(self) -> bool:
        """
        Click the sidebar's X button if it is present yet.

        Returns whether the click landed. close_ai_sidebar deliberately polls
        on sidebar state instead of this value -- what matters here is that a
        miss is a side-effect-free no-op, which is what makes retrying safe.
        """
        return bool(
            self.driver.execute_script("""
                const br = document.getElementById("ai-window-browser");
                const doc = br && br.contentDocument;
                if (!doc) return false;
                let hit = null;
                // aiWindow.html nests a few shadow roots deep to reach the
                // close button; 12 is headroom against further nesting while
                // still bounding a walk that would otherwise not terminate.
                (function walk(node, depth) {
                    if (!node || depth > 12) return;
                    for (const el of node.querySelectorAll("*")) {
                        if (el.matches('[data-l10n-id="aiwindow-close-sidebar"]')) {
                            hit = el;
                            return;
                        }
                        if (el.shadowRoot) {
                            walk(el.shadowRoot, depth + 1);
                            if (hit) return;
                        }
                    }
                })(doc, 0);
                if (!hit) return false;
                hit.click();
                return true;
            """)
        )
