from modules.page_base import BasePage


class MenuBar(BasePage):
    """Page Object Model for Menu Bar navigation"""

    @BasePage.context_chrome
    def activate_menu_bar(self) -> BasePage:
        """Enables the Menu Bar at the top of the window (if needed)"""
        if self.sys_platform() != "Darwin":
            self.context_click("toolbar-blank-space")
            self.click_and_hide_menu("menu-bar-checkbox")
        return self

    @BasePage.context_chrome
    def open_menu(self, menu_name: str) -> BasePage:
        """Opens a specified menu from the Menu Bar"""
        self.click_and_hide_menu(f"{menu_name.lower()}-menu-button")
        return self

    @BasePage.context_chrome
    def open_sidebar_panel_from_menu_bar(self, panel: str) -> BasePage:
        """Opens the specified sidebar panel via MenuBar > View > Sidebar > {panel}. Not supported on macOS (native
        menu bar is not accessible via WebDriver); callers should skip the test on macOS before calling this method.
        Argument: panel: The sidebar panel label as shown in the menu, e.g. "History", "Bookmarks", "Synced Tabs",
        "AI Chatbot", "Passwords". A matching "view-sidebar-{panel}" entry must exist in the components JSON.
        """
        self.activate_menu_bar()
        self.open_menu("View")
        self.click_on("view-sidebar-menu")
        self.click_and_hide_menu(f"view-sidebar-{panel.lower().replace(' ', '-')}")
        return self

    @BasePage.context_chrome
    def get_recently_closed_urls(self):
        """Opens History > Recently Closed Tabs and returns the URLs as a set"""
        self.activate_menu_bar()
        self.open_menu("History")
        self.click_on("menu-bar-recently-closed-tabs")
        items = self.get_elements("menu-bar-recently-closed-tabs-items")
        urls = {
            item.get_dom_attribute("targetURI")
            for item in items
            if item.get_dom_attribute("targetURI")
        }
        return urls
