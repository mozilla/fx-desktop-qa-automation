import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, Navigation, Sidebar, SplitView, TabBar

URLS = ["https://example.com/", "https://www.wikipedia.org/"]


@pytest.fixture()
def test_case():
    return "3903453"


@pytest.fixture()
def add_to_prefs_list():
    return [("browser.tabs.splitView.enabled", True)]


@pytest.mark.parametrize(
    "vertical_tabs, sidebar_expanded",
    [(False, None), (True, True), (True, False)],
    ids=["horizontal_tabs", "vertical_tabs_expanded", "vertical_tabs_collapsed"],
)
def test_split_view_single_tab_context_menu_horizontal_vertical(
    driver: Firefox, vertical_tabs: bool, sidebar_expanded: bool | None
):
    """
    C3903453 - Verify that the Split View context menu option is working when only one tab is selected in Horizontal and Vertical mode
    """

    tabs = TabBar(driver)
    context_menu = ContextMenu(driver)
    nav = Navigation(driver)
    sidebar = Sidebar(driver)
    split_view = SplitView(driver)

    # Enable vertical tabs, in the expanded or collapsed state, when required
    # for this parametrized case
    if vertical_tabs:
        nav.toggle_vertical_tabs()
        sidebar.expect_sidebar_expanded()
        if not sidebar_expanded:
            sidebar.click_sidebar_button()
            sidebar.expect_sidebar_expanded(False)

    tabs.open_urls_in_tabs(URLS, open_first_in_current_tab=True)
    tabs.wait_for_num_tabs(len(URLS))

    # Right-click one tab and use the Add Split View option
    tabs.create_split_view_from_tab(1, context_menu)

    # A Split View is created, with the tab on the left side
    split_view.expect_split_view_active()
    split_view.expect_panel_url(SplitView.LEFT, URLS[0])
    split_view.expect_panel_url(SplitView.RIGHT, "about:opentabs")
    assert split_view.count_tabs_in_split_view() == 2
