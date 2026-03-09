from modules.page_base import BasePage


class Sidebar(BasePage):
    """BOM for the Sidebar"""

    URL_TEMPLATE = ""

    def click_sidebar_button(self):
        """Click the sidebar toolbar button to toggle the sidebar open or closed"""
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
