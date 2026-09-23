import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, Navigation, SplitView, TabBar

URLS = ["about:about", "about:mozilla", "about:license"]

OPEN_TABS_URL = "about:opentabs"
SEARCH_TERM = "mozilla firefox"


@pytest.fixture()
def test_case():
    # C3903432 is split across two files: steps 1-5 here, steps 6-7 in
    # test_split_view_context_menu_select_searched_tab.py. Each needs its own
    # Split View, since the URL bar search replaces about:opentabs.
    return "3903432"


@pytest.fixture()
def add_to_prefs_list():
    return [("browser.tabs.splitView.enabled", True)]


def test_split_view_context_menu_search_single_tab(driver: Firefox):
    """
    C3903432 - Steps 1-5: Verify that a URL bar search from a Split View created
    from the context menu on a single tab opens on the right side.
    """
    tabs = TabBar(driver)
    context_menu = ContextMenu(driver)
    nav = Navigation(driver)
    split_view = SplitView(driver)

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

    # Search for something inside the URL bar in the right view and confirm
    nav.search(SEARCH_TERM)

    # The searched item is correctly opened on the right side of the split view,
    # and the left side is left alone
    split_view.expect_panel_url_contains(SplitView.RIGHT, "mozilla")
    assert split_view.get_panel_url(SplitView.RIGHT) != OPEN_TABS_URL
    assert split_view.get_panel_url(SplitView.LEFT) == URLS[0]
