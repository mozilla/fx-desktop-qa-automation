import logging
from typing import Literal

from selenium.common.exceptions import TimeoutException
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

    def expect_first_run_view(self, active: bool = True) -> BasePage:
        """
        Wait until the window is (or is not) showing the Smart Window first-run
        view, which hides the nav-bar while onboarding is on screen.
        """
        self.expect(
            lambda _: (
                self.get_element("main-window").get_attribute("aiwindow-first-run")
                is not None
            )
            == active
        )
        return self

    # ── Account ──────────────────────────────────────────────────────────

    def open_smart_window_sign_in(self) -> BasePage:
        """
        Choose Smart in the Switch Windows panel while signed out, then switch
        the driver to the FxA sign-in tab that Firefox opens for Smart Window.
        """
        num_tabs = len(self.driver.window_handles)
        self.click_switch_to_smart_window()
        self.wait_for_num_tabs(num_tabs + 1)
        self.switch_to_new_tab()
        self.expect_selected_tab_url_contains("service=smartwindow")
        return self

    def expect_signed_in(self) -> BasePage:
        """
        Wait until Firefox reports the FxA account as signed in.
        """
        self.element_attribute_is("main-window", "fxastatus", "signedin")
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

        The button is several shadow roots inside
        <browser id="ai-window-browser">, which components.json cannot
        traverse, so the walk runs in privileged JS and matches on
        data-l10n-id to stay locale-independent.

        Raises
        ------
        AssertionError
            If the sidebar is still open when the wait expires; the message
            names the cause.
        """
        # This predicate clicks, which is unusual and only safe because the X
        # is close-only -- do not copy it for a toggle. The retry is needed
        # because the container is visible before the inner document loads,
        # and clicks landing there are dropped (observed 9/10 without).
        clicked_at_least_once = False
        walk_was_truncated = False

        def _closed(_) -> bool:
            nonlocal clicked_at_least_once, walk_was_truncated
            if not self.ai_sidebar_open():
                return True
            result = self._click_sidebar_close_button()
            if result == "truncated":
                # Retried, not raised: the cut branch may not be the button's.
                walk_was_truncated = True
            if not result and not clicked_at_least_once:
                # The button vanishes as the sidebar animates shut, so misses
                # after a landed click are expected.
                logging.debug("sidebar close button not reachable yet, will retry")
            # `is True`: "truncated" is truthy and would fake a landed click.
            clicked_at_least_once = clicked_at_least_once or result is True
            return False

        try:
            self.expect(_closed)
        except TimeoutException:
            cause = (
                "the X button was clicked but the sidebar stayed open"
                if clicked_at_least_once
                else "the X button never appeared inside ai-window-browser"
            )
            if walk_was_truncated and not clicked_at_least_once:
                cause += (
                    ", and the shadow walk hit its depth cap of 12 at least "
                    "once, so the button may be nested below it"
                )
            raise AssertionError(f"AI chat sidebar did not close: {cause}") from None
        return self

    @BasePage.context_chrome
    def _click_sidebar_close_button(self) -> Literal[True, False, "truncated"]:
        """
        Click the sidebar's X button if it is present yet.

        Returns
        -------
        Literal[True, False, "truncated"]
            True if the click landed, False if the button is not in the tree
            yet, "truncated" if the walk hit its depth cap first.

        Callers should poll sidebar state rather than this value; a miss is a
        side-effect-free no-op, which is what makes retrying safe.
        """
        return self.driver.execute_script("""
            const br = document.getElementById("ai-window-browser");
            const doc = br && br.contentDocument;
            if (!doc) return false;
            let hit = null;
            let truncated = false;
            // `depth` counts shadow-boundary crossings, not DOM depth; 12 is
            // ample for aiWindow.html while still bounding the walk.
            (function walk(node, depth) {
                if (!node) return;
                if (depth > 12) { truncated = true; return; }
                for (const el of node.querySelectorAll("*")) {
                    if (el.matches('[data-l10n-id="aiwindow-close-sidebar"]')) {
                        hit = el;
                        return;
                    }
                    if (el.shadowRoot) {
                        walk(el.shadowRoot, depth + 1);
                        // Bail on a hit only -- a sibling branch may still
                        // hold the button. Do not add a `truncated` exit here.
                        if (hit) return;
                    }
                }
            })(doc, 0);
            if (!hit) return truncated ? "truncated" : false;
            hit.click();
            return true;
        """)
