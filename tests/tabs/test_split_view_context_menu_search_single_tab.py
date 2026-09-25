import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, Navigation, SplitView, TabBar
from modules.page_object import AboutOpentabs

URLS = ["about:about", "about:mozilla", "about:license"]
SEARCH_TERM = "mozilla firefox"

OPEN_TABS_URL = "about:opentabs"
SECOND_SPLIT_TAB = "The Book of Mozilla, 6:27"
TAB_TO_SEARCH_FOR = "Licenses"
TAB_TO_SEARCH_FOR_URL = "about:license"


@pytest.fixture()
def test_case():
    return "3903432"


@pytest.fixture()
def add_to_prefs_list():
    return [("browser.tabs.splitView.enabled", True)]


def test_split_view_context_menu_search_single_tab(driver: Firefox):
    """
    C3903432 - Verify that searches from a Split View created from the context
    menu on a single tab open on the right side.
    """
    tabs = TabBar(driver)
    context_menu = ContextMenu(driver)
    nav = Navigation(driver)
    split_view = SplitView(driver)
    open_tabs = AboutOpentabs(driver)

    # Ensure that multiple open tabs are present
    tabs.open_urls_in_tabs(URLS, open_first_in_current_tab=True)
    tabs.wait_for_num_tabs(len(URLS))

    # Create a Split view using the Context menu option on a single tab
    tabs.create_split_view_from_tab(1, context_menu)

    # The Split View is created with the previously selected tab displayed on
    # the left side
    split_view.expect_split_view_active()
    split_view.expect_panel_url(SplitView.LEFT, URLS[0])

    # Search for something inside the URL bar in the right view and confirm
    nav.search(SEARCH_TERM)

    # The searched item is correctly opened on the right side of the split view
    split_view.expect_panel_url_contains(SplitView.RIGHT, "mozilla")

    # Repeat step 1 and search for an opened tab inside the about:opentabs page
    # and select it
    tabs.create_split_view_from_tab(SECOND_SPLIT_TAB, context_menu)
    split_view.expect_panel_url(SplitView.RIGHT, OPEN_TABS_URL)
    split_view.switch_to_panel(SplitView.RIGHT)
    open_tabs.search_tabs(TAB_TO_SEARCH_FOR)
    open_tabs.expect_listed_tab_titles([TAB_TO_SEARCH_FOR])
    open_tabs.select_tab_by_title(TAB_TO_SEARCH_FOR)

    # The searched tab is correctly opened on the right side of the split view
    split_view.expect_panel_url(SplitView.RIGHT, TAB_TO_SEARCH_FOR_URL)
