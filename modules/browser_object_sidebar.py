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
    def expect_extension_pinned_to_sidebar(self, extension_id: str):
        """Verify the extension button is present in the sidebar strip.

        JS pierces the open shadow root of <sidebar-main> and checks extensionId
        entirely in the script. The label attribute is not set on these buttons —
        identity is confirmed by extensionId alone. Python's get_attribute() on
        chrome-context WebElements returned from JS returns None via GeckoDriver,
        so the comparison must stay inside the JS call.
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

        JS pierces the open shadow root of <sidebar-main>, finds the moz-button
        by view attribute, and clicks it — all within the script. See
        expect_extension_pinned_to_sidebar for why attribute access must stay in JS.
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

    @BasePage.context_chrome
    def click_manage_extensions(self):
        """Click the Manage Extensions link in the Customize Sidebar panel.

        The customize panel loads in <browser id="sidebar"> as sidebar-customize.html.
        That page uses Lit web components with nested shadow roots. JS recursively
        pierces all shadow roots in contentDocument to find and click the link.
        Waits for the document to be fully loaded before searching.
        The link opens about:addons in a new tab — call switch_to_new_tab() after
        (inherited from BasePage).
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
