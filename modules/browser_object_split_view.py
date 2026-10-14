from typing import Union

from selenium.common.exceptions import TimeoutException

from modules.browser_object_context_menu import ContextMenu
from modules.browser_object_tabbar import TabBar
from modules.page_base import BasePage
from modules.page_object_about_pages import AboutOpentabs


class SplitView(BasePage):
    """
    Browser Object Model for Split View: the two side-by-side content panels,
    the divider between them, and the tab strip wrapper grouping their tabs.

    Panels are addressed by column, where 0 is the left side and 1 is the right
    side. Use create_split_view to create one.
    """

    URL_TEMPLATE = "about:blank"

    LEFT = "0"
    RIGHT = "1"

    # Footer menu options, by the command they run
    SEPARATE_TABS = "separateTabs"
    REVERSE_TABS = "reverseTabs"
    CLOSE_BOTH_TABS = "closeTabs"

    def create_split_view(
        self, left_tab: Union[str, int], right_tab_title: str
    ) -> BasePage:
        """
        Create a Split View holding two open tabs: `left_tab` (a title or an
        index) on the left side and the tab titled `right_tab_title` on the right.
        """
        TabBar(self.driver).create_split_view_from_tab(
            left_tab, ContextMenu(self.driver)
        )
        self.expect_split_view_active()

        # The right side opens on about:opentabs, pick the second tab from there
        self.expect_panel_url(self.RIGHT, "about:opentabs")
        self.switch_to_panel(self.RIGHT)
        AboutOpentabs(self.driver).select_tab_by_title(right_tab_title)
        self.expect(lambda _: self.get_panel_title(self.RIGHT) == right_tab_title)
        return self

    @BasePage.context_chrome
    def get_footer_menu_state(self) -> str:
        """Return the state of the footer menu: closed, showing, open or hiding."""
        return self.driver.execute_script(
            "return document.getElementById('split-view-menu')?.state ?? 'closed';"
        )

    @BasePage.context_chrome
    def open_footer_menu(self) -> BasePage:
        """
        Open the three-dot menu in the Split View footer. The footer, with the
        button at its right corner, is only shown on the side that is not
        selected.
        """
        column = self.RIGHT if self.get_selected_column() == self.LEFT else self.LEFT
        self.element_visible("split-view-footer-menu-button", labels=[column])
        self.click_on("split-view-footer-menu-button", labels=[column])

        # Read the popup state, as headless Firefox never sets its open attribute
        try:
            self.expect(lambda _: self.get_footer_menu_state() == "open")
        except TimeoutException:
            raise AssertionError(
                "Split View footer menu did not open, its state is "
                f"{self.get_footer_menu_state()!r}"
            )
        return self

    def select_footer_menu_option(self, command: str) -> BasePage:
        """
        Pick an option from the Split View footer menu, by command:
        SEPARATE_TABS, REVERSE_TABS or CLOSE_BOTH_TABS.
        """
        self.open_footer_menu()
        self.click_and_hide_menu("split-view-menuitem", labels=[command])
        return self

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

        The tab is matched by URL, so the panel's URL must be unique across all
        open tabs.
        """
        url = self.get_panel_url(column)
        with self.driver.context(self.driver.CONTEXT_CONTENT):
            matches = []
            for handle in self.driver.window_handles:
                self.driver.switch_to.window(handle)
                if self.driver.current_url == url:
                    matches.append(handle)
            assert len(matches) == 1, (
                f"Expected exactly one tab loaded with {url}, found {len(matches)}"
            )
            self.driver.switch_to.window(matches[0])
        return self

    def expect_panel_url(self, column: str, url: str) -> BasePage:
        """Wait until the panel in `column` has loaded exactly `url`."""
        self.expect(lambda _: self.get_panel_url(column) == url)
        return self

    def expect_panel_url_contains(self, column: str, fragment: str) -> BasePage:
        """Wait until the URL of the panel in `column` contains `fragment`."""
        self.expect(lambda _: fragment in self.get_panel_url(column))
        return self
