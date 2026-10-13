import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, Navigation, SplitView, TabBar
from modules.page_object import AboutOpentabs

URLS = ["https://www.youtube.com", "https://www.wikipedia.org"]
SECOND_SPLIT_TAB = "Wikipedia"
NEW_TAB_URL = "https://example.com/"
NEW_TAB_SEARCH = "example"
OTHER_WINDOW_URL = "https://www.mozilla.org/"
OTHER_WINDOW_SEARCH = "mozilla"
MOVE_TAB_ACTION = "Move Tab to Split View"


@pytest.fixture()
def test_case():
    return "3903450"


@pytest.fixture()
def add_to_prefs_list():
    return [("browser.tabs.splitView.enabled", True)]


def test_move_tab_to_split_view(driver: Firefox):
    """
    C3903450 - Verify that the `Move tab to Split View` option works correctly
    """

    tabs = TabBar(driver)
    context_menu = ContextMenu(driver)
    nav = Navigation(driver)
    split_view = SplitView(driver)
    open_tabs = AboutOpentabs(driver)

    # Open Youtube and Wikipedia and use the Add Split View context menu option
    # on the Youtube tab
    tabs.open_urls_in_tabs(URLS, open_first_in_current_tab=True)
    tabs.wait_for_num_tabs(len(URLS))
    tabs.create_split_view_from_tab(1, context_menu)
    split_view.expect_split_view_active()
    split_view.expect_panel_url_contains(SplitView.LEFT, "youtube.com")

    # Click the Wikipedia tab, it is moved into Split View
    split_view.expect_panel_url(SplitView.RIGHT, "about:opentabs")
    split_view.switch_to_panel(SplitView.RIGHT)
    open_tabs.select_tab_by_title(SECOND_SPLIT_TAB)
    split_view.expect_panel_url_contains(SplitView.RIGHT, "wikipedia.org")

    # Open a new tab and focus one of the views from the Split View
    tabs.new_tab_by_button()
    tabs.wait_for_num_tabs(len(URLS) + 1)
    tabs.switch_to_new_tab()
    driver.get(NEW_TAB_URL)
    tabs.click_tab_by_index(1)
    split_view.expect_split_view_active()

    # Search for the new tab in the URL bar, its result reads Move Tab to Split View
    nav.type_in_awesome_bar(NEW_TAB_SEARCH)
    nav.expect_switch_tab_action_text(NEW_TAB_SEARCH, MOVE_TAB_ACTION)

    # Click the result, the tab is moved into Split View in place of the focused view
    nav.click_switch_tab_result(NEW_TAB_SEARCH)
    split_view.expect_panel_url(SplitView.LEFT, NEW_TAB_URL)
    split_view.expect_panel_url_contains(SplitView.RIGHT, "wikipedia.org")
    assert split_view.count_tabs_in_split_view() == 2

    # Verify the Move Tab to Split View option works for a tab from another window
    original_tab = driver.current_window_handle
    driver.switch_to.new_window("window")
    driver.get(OTHER_WINDOW_URL)
    driver.switch_to.window(original_tab)
    tabs.click_tab_by_index(2)
    split_view.expect_split_view_active()

    nav.type_in_awesome_bar(OTHER_WINDOW_SEARCH)
    nav.expect_switch_tab_action_text(OTHER_WINDOW_SEARCH, MOVE_TAB_ACTION)
    nav.click_switch_tab_result(OTHER_WINDOW_SEARCH)
    split_view.expect_panel_url_contains(SplitView.RIGHT, "mozilla.org")
    split_view.expect_panel_url(SplitView.LEFT, NEW_TAB_URL)
    assert split_view.count_tabs_in_split_view() == 2
