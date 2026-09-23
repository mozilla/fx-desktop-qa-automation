from modules.page_base import BasePage


class SplitView(BasePage):
    """
    Browser Object Model for Split View: the two side-by-side content panels,
    the divider between them, and the tab strip wrapper grouping their tabs.

    Panels are addressed by column, where 0 is the left side and 1 is the right
    side. Use TabBar.create_split_view_from_tab to create one.
    """

    URL_TEMPLATE = "about:blank"

    LEFT = "0"
    RIGHT = "1"

    def expect_split_view_active(self, active: bool = True) -> BasePage:
        """Wait until the window does (or does not) have a Split View."""
        if active:
            self.element_exists("split-view-tabpanels")
        else:
            self.element_does_not_exist("split-view-tabpanels")
        return self

    @BasePage.context_chrome
    def count_tabs_in_split_view(self) -> int:
        """Return the number of tabs currently sitting in a Split View."""
        return len(self.get_elements("split-view-wrapper-tab"))

    @BasePage.context_chrome
    def get_selected_column(self) -> str:
        """
        Return the column of the selected Split View panel, i.e. the one the
        Awesome Bar and the toolbar act on.
        """
        column = self.driver.execute_script(
            "return document.documentElement.getAttribute('splitview-selected-column');"
        )
        assert column is not None, "No Split View panel is selected"
        return column

    @BasePage.context_chrome
    def get_panel_url(self, column: str) -> str:
        """
        Return the URL loaded in the Split View panel in `column`.

        Read from the panel's own browser rather than driver.current_url, since
        the content context only ever points at the selected panel.
        """
        panel = self.get_element("split-view-panel", labels=[column])
        return self.driver.execute_script(
            "return arguments[0].querySelector('browser').currentURI.spec;", panel
        )

    @BasePage.context_chrome
    def get_panel_title(self, column: str) -> str:
        """Return the page title shown on the tab driving the panel in `column`."""
        panel = self.get_element("split-view-panel", labels=[column])
        tab = self.get_element(
            "tab-by-linked-panel", labels=[panel.get_attribute("id")]
        )
        return tab.get_attribute("label")

    def switch_to_panel(self, column: str) -> BasePage:
        """
        Point the content context at the tab shown in the panel in `column`, so
        that page objects act on that side of the Split View.
        """
        url = self.get_panel_url(column)
        with self.driver.context(self.driver.CONTEXT_CONTENT):
            for handle in self.driver.window_handles:
                self.driver.switch_to.window(handle)
                if self.driver.current_url == url:
                    return self
        raise AssertionError(f"No tab is loaded with {url}")

    def expect_panel_url(self, column: str, url: str) -> BasePage:
        """Wait until the panel in `column` has loaded exactly `url`."""
        self.expect(lambda _: self.get_panel_url(column) == url)
        return self

    def expect_panel_url_contains(self, column: str, fragment: str) -> BasePage:
        """Wait until the URL of the panel in `column` contains `fragment`."""
        self.expect(lambda _: fragment in self.get_panel_url(column))
        return self
