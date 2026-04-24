from modules.page_base import BasePage


class Sidebar(BasePage):
    """BOM for the Sidebar"""

    URL_TEMPLATE = ""

    def click_sidebar_button(self):
        """Click the sidebar toolbar button to toggle the sidebar open or closed"""
        self.element_clickable("sidebar-button")
        self.click_on("sidebar-button")
        return self

    def expect_sidebar_open(self):
        """Verify the sidebar is open: button tooltiptext changes to 'Hide sidebar'"""
        self.element_attribute_contains("sidebar-button", "tooltiptext", "Hide sidebar")
        return self

    def expect_sidebar_closed(self):
        """Verify the sidebar is closed: button tooltiptext changes to 'Show sidebar'"""
        self.element_attribute_contains("sidebar-button", "tooltiptext", "Show sidebar")
        return self

    def hide_sidebar_via_context_menu(self):
        """Right-click the sidebar panel and select Hide Sidebar from the context menu"""
        self.context_click("sidebar-main")
        self.click_and_hide_menu("sidebar-hide-option")
        return self

    @BasePage.context_chrome
    def move_sidebar_to_right(self) -> BasePage:
        """Move the sidebar to the right side by setting sidebar.position_start to False."""
        self.driver.execute_script(
            "Services.prefs.setBoolPref('sidebar.position_start', false);"
        )
        return self

    @BasePage.context_chrome
    def expect_extension_pinned_to_sidebar(self, extension_id: str):
        """Verify the extension button is present in the sidebar strip.

        JS pierces the open shadow root of <sidebar-main> and checks extensionId entirely in the script. The label
        attribute is not set on these buttons — identity is confirmed by extensionId alone. Python's get_attribute()
        on chrome-context WebElements returned from JS returns None via GeckoDriver, so the comparison must stay
        inside the JS call.
        """

        def _verify(_):
            return self.driver.execute_script(
                "return Array.from("
                "  document.querySelector('sidebar-main')?.shadowRoot"
                "  ?.querySelectorAll('moz-button') || []"
                ").some(b => b.getAttribute('extensionId') === arguments[0]);",
                extension_id,
            )

        self.custom_wait(timeout=30).until(_verify)
        return self

    @BasePage.context_chrome
    def click_customize_sidebar(self):
        """Click the Customize Sidebar button to open the customize panel.

        JS pierces the open shadow root of <sidebar-main>, finds the moz-button by view attribute, and clicks it —
        all within the script. See expect_extension_pinned_to_sidebar for why attribute access must stay in JS.
        """
        self.wait.until(
            lambda _: self.driver.execute_script(
                "const btn = Array.from("
                "  document.querySelector('sidebar-main')?.shadowRoot"
                "  ?.querySelectorAll('moz-button') || []"
                ").find(b => b.getAttribute('view') === 'viewCustomizeSidebar');"
                "if (btn) { btn.click(); return true; }",
            )
        )
        return self

    def _exec_on_vertical_tab_element(self, js_on_element: str):
        """Find the Vertical tabs checkbox in the customize panel and evaluate js_on_element on it.

        Shared boilerplate for all Vertical tabs checkbox interactions. Accesses browser#sidebar
        contentDocument, recursively pierces shadow roots, finds [data-l10n-id*="vertical-tab"], and
        evaluates js_on_element with el in scope. Returns null if the panel is not ready or the element
        is not found; otherwise returns the result of js_on_element. Both null and false are falsy, so
        wait.until retries in either case — null on miss is a consistency choice, not a semantic one.

        Must be called from within a @BasePage.context_chrome method.
        """
        return self.driver.execute_script(
            "const cd = document.querySelector('browser#sidebar')?.contentDocument;"
            "if (!cd || cd.readyState !== 'complete') return null;"
            "function search(root) {"
            "  const el = root.querySelector('[data-l10n-id*=\"vertical-tab\"]');"
            "  if (el) return " + js_on_element + ";"
            "  for (const host of root.querySelectorAll('*')) {"
            "    if (host.shadowRoot) {"
            "      const r = search(host.shadowRoot);"
            "      if (r !== null) return r;"
            "    }"
            "  }"
            "  return null;"
            "}"
            "return search(cd);"
        )

    def _exec_on_element_by_l10n_id(self, l10n_id: str, js_on_element: str):
        """Find a customize-panel element by exact data-l10n-id and evaluate js_on_element on it.

        General-purpose version of _exec_on_vertical_tab_element. l10n_id is passed as a JS
        argument to avoid string injection; js_on_element is a developer-controlled code expression
        concatenated at call time. Returns null if the panel is not ready or the element is not found.

        Must be called from within a @BasePage.context_chrome method.
        """
        return self.driver.execute_script(
            "const l10nId = arguments[0];"
            "const cd = document.querySelector('browser#sidebar')?.contentDocument;"
            "if (!cd || cd.readyState !== 'complete') return null;"
            "function search(root) {"
            "  const el = root.querySelector('[data-l10n-id=\"' + l10nId + '\"]');"
            "  if (el) return " + js_on_element + ";"
            "  for (const host of root.querySelectorAll('*')) {"
            "    if (host.shadowRoot) {"
            "      const r = search(host.shadowRoot);"
            "      if (r !== null) return r;"
            "    }"
            "  }"
            "  return null;"
            "}"
            "return search(cd);",
            l10n_id,
        )

    @BasePage.context_chrome
    def expect_vertical_tabs_checkbox_visible(self):
        """Verify that the Vertical tabs checkbox is displayed in the Sidebar settings section of the customize panel."""
        self.wait.until(lambda _: self._exec_on_vertical_tab_element("true"))
        return self

    @BasePage.context_chrome
    def click_vertical_tabs_checkbox(self):
        """Click the Vertical tabs checkbox in the Sidebar settings section of the customize panel."""
        self.wait.until(
            lambda _: self._exec_on_vertical_tab_element("(el.click(), true)")
        )
        return self

    @BasePage.context_chrome
    def expect_vertical_tabs_active(self):
        """Verify that vertical tabs are active by checking that the Vertical tabs checkbox is checked.

        The Vertical tabs checkbox remains visible in the panel at all times; when checked, vertical tabs
        are active. Mirrors expect_horizontal_tabs_active which verifies the unchecked state.
        """
        self.wait.until(
            lambda _: self._exec_on_vertical_tab_element("el.checked === true")
        )
        return self

    @BasePage.context_chrome
    def expect_horizontal_tabs_active(self):
        """Verify that horizontal tabs are active by checking that the Vertical tabs checkbox is unchecked.

        There is no dedicated UI element for horizontal tabs — the mode is defined purely by the absence of
        vertical tabs. The Vertical tabs checkbox remains visible in the panel at all times; when unchecked,
        horizontal tabs are active.
        """
        self.wait.until(
            lambda _: self._exec_on_vertical_tab_element("el.checked === false")
        )
        return self

    @BasePage.context_chrome
    def click_expand_on_hover_in_panel(self) -> BasePage:
        """Click the 'Expand sidebar on hover' checkbox in the Customize Sidebar panel."""
        self.wait.until(
            lambda _: self._exec_on_element_by_l10n_id(
                "expand-sidebar-on-hover", "(el.click(), true)"
            )
        )
        return self

    @BasePage.context_chrome
    def click_move_sidebar_to_right_in_panel(self) -> BasePage:
        """Click the 'Move sidebar to the right' checkbox in the Customize Sidebar panel."""
        self.wait.until(
            lambda _: self._exec_on_element_by_l10n_id(
                "sidebar-show-on-the-right", "(el.click(), true)"
            )
        )
        return self

    @BasePage.context_chrome
    def get_sidebar_strip_width(self) -> float:
        """Return the current rendered width of the sidebar-main element in pixels."""
        return self.driver.execute_script(
            "return document.querySelector('sidebar-main')?.getBoundingClientRect().width ?? 0;"
        )

    @BasePage.context_chrome
    def expect_sidebar_strip_collapsed(self) -> "Sidebar":
        """Wait until the sidebar strip width has stabilized to its collapsed state.

        Polls until two consecutive readings (500 ms apart) return the same non-zero
        width, ensuring any panel-close animation has finished before the caller
        proceeds to measure a baseline width.
        """
        last: list[float | None] = [None]

        def _stable(_):
            w = self.get_sidebar_strip_width()
            if w > 0 and w == last[0]:
                return True
            last[0] = w
            return False

        self.wait.until(_stable)
        return self

    @BasePage.context_chrome
    def expect_expand_on_hover_unavailable(self):
        """Wait until the expand-on-hover option is no longer available.

        After switching from vertical tabs to horizontal tabs, the option should
        disappear from the Customize Sidebar panel. If it is still present, it must
        at least be hidden or disabled.
        """

        def _is_unavailable(_):
            state = self.driver.execute_script(
                "const cd = document.querySelector('browser#sidebar')?.contentDocument;"
                "if (!cd || cd.readyState !== 'complete') return 'not-ready';"
                "function search(root) {"
                "  const el = root.querySelector('[data-l10n-id*=\"expand-on-hover\"]');"
                "  if (el) return el.disabled === true || el.hidden === true || !el.offsetParent;"
                "  for (const host of root.querySelectorAll('*')) {"
                "    if (host.shadowRoot) {"
                "      const result = search(host.shadowRoot);"
                "      if (result !== 'not-found') return result;"
                "    }"
                "  }"
                "  return 'not-found';"
                "}"
                "return search(cd);"
            )
            return state == "not-found" or state is True

        self.wait.until(_is_unavailable)
        return self

    @BasePage.context_chrome
    def close_ai_chat_panel(self) -> "Sidebar":
        """Close the AI chat panel by clicking its close button.

        The close button (button#main-button[title='Close']) lives inside Lit web components
        behind nested shadow DOM in browser#sidebar's contentDocument. JS recursively pierces
        shadow roots to find and click it — Selenium cannot reach inside shadow DOM directly.
        """
        self.wait.until(
            lambda _: self.driver.execute_script(
                "const cd = document.querySelector('browser#sidebar')?.contentDocument;"
                "if (!cd || cd.readyState !== 'complete') return false;"
                "function search(root) {"
                "  const btn = root.querySelector('button#main-button[title=\"Close\"]');"
                "  if (btn) { btn.click(); return true; }"
                "  for (const host of root.querySelectorAll('*')) {"
                "    if (host.shadowRoot && search(host.shadowRoot)) return true;"
                "  }"
                "  return false;"
                "}"
                "return search(cd);"
            )
        )
        return self

    @BasePage.context_chrome
    def expect_ai_chat_panel_open(self) -> "Sidebar":
        """Verify the AI chat panel is loaded in the sidebar by checking for the onboarding root."""
        self.wait.until(
            lambda _: self.driver.execute_script(
                "const cd = document.querySelector('browser#sidebar')?.contentDocument;"
                "return cd?.readyState === 'complete' && "
                "Boolean(cd?.querySelector('#multi-stage-message-root'));"
            )
        )
        return self

    @BasePage.context_chrome
    def expect_ai_providers_displayed(self) -> "Sidebar":
        """Verify that AI provider radio options are shown in the chatbot onboarding panel."""
        self.wait.until(
            lambda _: self.driver.execute_script(
                "const cd = document.querySelector('browser#sidebar')?.contentDocument;"
                "if (!cd || cd.readyState !== 'complete') return false;"
                "return cd.querySelectorAll('input[type=\"radio\"]').length > 0;"
            )
        )
        return self

    @BasePage.context_chrome
    def select_first_ai_provider(self) -> "Sidebar":
        """Select the first AI provider via its label and confirm with the Continue button.

        The radio inputs are sr-only so the enclosing label must be clicked instead.
        Waits until the onboarding screen is gone, confirming the provider was saved.
        """
        self.wait.until(
            lambda _: self.driver.execute_script(
                "const cd = document.querySelector('browser#sidebar')?.contentDocument;"
                "if (!cd || cd.readyState !== 'complete') return false;"
                "const label = cd.querySelector('label.select-item');"
                "if (!label) return false;"
                "label.click();"
                "return true;"
            )
        )
        self.wait.until(
            lambda _: self.driver.execute_script(
                "const cd = document.querySelector('browser#sidebar')?.contentDocument;"
                "if (!cd || cd.readyState !== 'complete') return false;"
                "const continueBtn = cd.querySelector('button[value=\"primary_button\"]');"
                "if (!continueBtn) return false;"
                "continueBtn.click();"
                "return true;"
            )
        )
        self.wait.until(
            lambda _: self.driver.execute_script(
                "const cd = document.querySelector('browser#sidebar')?.contentDocument;"
                "if (!cd || cd.readyState !== 'complete') return false;"
                "if (cd.querySelector('#multi-stage-message-root')) return false;"
                "try { return !!Services.prefs.getStringPref('browser.ml.chat.provider', ''); }"
                "catch(e) { return false; }"
            )
        )
        return self

    @BasePage.context_chrome
    def expect_ai_chat_sidebar_open(self):
        """Verify the sidebar is open and showing the AI Chat panel."""
        self.element_attribute_contains(
            "sidebar-box", "sidebarcommand", "viewGenaiChatSidebar"
        )
        return self

    @BasePage.context_chrome
    def expect_summarize_button_visible(self) -> "Sidebar":
        """Verify the Summarize page button is visible in the AI Chat panel.

        The button lives inside <browser id="sidebar">'s contentDocument (chrome://browser/content/genai/chat.html).
        Selenium has no API to switch into an embedded XUL <browser> element, so JS is used to access
        contentDocument and query the button directly.
        """
        self.wait.until(
            lambda _: self.driver.execute_script(
                "const cd = document.querySelector('browser#sidebar')?.contentDocument;"
                "if (!cd) return false;"
                "return cd.getElementById('summarize-button') !== null;"
            )
        )
        return self

    @BasePage.context_chrome
    def click_manage_extensions(self):
        """Click the Manage Extensions link in the Customize Sidebar panel.

        The customize panel loads in <browser id="sidebar"> as sidebar-customize.html. That page uses Lit web
        components with nested shadow roots. JS recursively pierces all shadow roots in contentDocument to find and
        click the link. Waits for the document to be fully loaded before searching. The link opens about:addons in a
        new tab.
        """
        self.wait.until(
            lambda _: self.driver.execute_script(
                "const cd = document.querySelector('browser#sidebar')?.contentDocument;"
                "if (!cd || cd.readyState !== 'complete') return null;"
                "function search(root) {"
                "  const el = root.querySelector('a[data-l10n-id=\"sidebar-manage-extensions\"]');"
                "  if (el) { el.click(); return true; }"
                "  for (const host of root.querySelectorAll('*')) {"
                "    if (host.shadowRoot && search(host.shadowRoot)) return true;"
                "  }"
                "  return false;"
                "}"
                "return search(cd) || null;"
            )
        )
        return self
