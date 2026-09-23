import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, SplitView, TabBar
from modules.page_object import AboutOpentabs

URLS = ["about:about", "about:mozilla", "about:license"]
TAB_TITLES = ["The Book of Mozilla, 6:27", "Licenses"]

OPEN_TABS_URL = "about:opentabs"
TAB_TO_SEARCH_FOR = "Licenses"
TAB_TO_SEARCH_FOR_URL = "about:license"


@pytest.fixture()
def test_case():
    return "3903432"


@pytest.fixture()
def add_to_prefs_list():
    return [("browser.tabs.splitView.enabled", True)]


def test_split_view_context_menu_select_searched_tab(driver: Firefox):
    """
    C3903432 - Steps 1-3, 6-7: Verify that an open tab searched for and selected
    in the about:opentabs page opens on the right side of a Split View created
    from the context menu on a single tab.
    """
    tabs = TabBar(driver)
    context_menu = ContextMenu(driver)
    split_view = SplitView(driver)
    open_tabs = AboutOpentabs(driver)

    # Ensure that multiple open tabs are present
    tabs.open_urls_in_tabs(URLS, open_first_in_current_tab=True)
    tabs.wait_for_num_tabs(len(URLS))

    # Create a Split view using the Context menu option on a single tab
    tabs.create_split_view_from_tab(1, context_menu)

    # The Split View is created with the previously selected tab displayed on
    # the left side, and about:opentabs opened and selected on the right
    split_view.expect_split_view_active()
    assert split_view.count_tabs_in_split_view() == 2
    split_view.expect_panel_url(SplitView.LEFT, URLS[0])
    split_view.expect_panel_url(SplitView.RIGHT, OPEN_TABS_URL)
    assert split_view.get_selected_column() == SplitView.RIGHT

    # Search for an opened tab inside the about:opentabs page and select it.
    # Only the tabs left out of the Split View are offered.
    split_view.switch_to_panel(SplitView.RIGHT)
    open_tabs.expect_listed_tab_titles(TAB_TITLES)
    open_tabs.search_tabs(TAB_TO_SEARCH_FOR)
    open_tabs.expect_listed_tab_titles([TAB_TO_SEARCH_FOR])
    open_tabs.select_tab_by_title(TAB_TO_SEARCH_FOR)

    # The searched tab is correctly opened on the right side of the split view,
    # taking the place of the tab picker
    split_view.expect_panel_url(SplitView.RIGHT, TAB_TO_SEARCH_FOR_URL)
    assert split_view.get_panel_title(SplitView.RIGHT) == TAB_TO_SEARCH_FOR
    assert split_view.get_panel_url(SplitView.LEFT) == URLS[0]
    assert split_view.count_tabs_in_split_view() == 2
