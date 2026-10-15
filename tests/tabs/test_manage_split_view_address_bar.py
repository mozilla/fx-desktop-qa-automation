import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, SplitView, TabBar
from modules.page_object import AboutOpentabs

URLS = ["about:about", "about:mozilla", "about:license", "about:robots"]
FIRST_SPLIT_TAB = "The Book of Mozilla, 6:27"
SECOND_SPLIT_TAB = "Gort! Klaatu barada nikto!"


@pytest.fixture()
def test_case():
    return "3903448"


@pytest.fixture()
def add_to_prefs_list():
    return [("browser.tabs.splitView.enabled", True)]


def test_manage_split_view_address_bar(driver: Firefox):
    """
    C3903448 - Verify that Split View can be managed using the Address bar button
    """
    tabs = TabBar(driver)
    context_menu = ContextMenu(driver)
    split_view = SplitView(driver)
    open_tabs = AboutOpentabs(driver)

    # Ensure multiple Split Views are created
    tabs.open_urls_in_tabs(URLS, open_first_in_current_tab=True)
    tabs.wait_for_num_tabs(len(URLS))

    tabs.create_split_view_from_tab(1, context_menu)
    split_view.expect_panel_url(SplitView.RIGHT, "about:opentabs")
    split_view.switch_to_panel(SplitView.RIGHT)
    open_tabs.select_tab_by_title(FIRST_SPLIT_TAB)
    split_view.expect_panel_url(SplitView.RIGHT, URLS[1])

    tabs.create_split_view_from_tab(3, context_menu)
    split_view.expect_panel_url(SplitView.RIGHT, "about:opentabs")
    split_view.switch_to_panel(SplitView.RIGHT)
    open_tabs.select_tab_by_title(SECOND_SPLIT_TAB)
    split_view.expect_panel_url(SplitView.RIGHT, URLS[3])

    split_view.expect_split_view_count(2)
    tabs.wait_for_num_tabs(len(URLS))

    # Select one Split View and pick Separate Tabs from the address bar button,
    # the Split View is broken up while both tabs stay open
    tabs.click_tab_by_index(1)
    split_view.select_urlbar_menu_option(SplitView.SEPARATE_TABS)
    split_view.expect_split_view_count(1)
    split_view.expect_split_view_active(False)
    tabs.wait_for_num_tabs(len(URLS))

    # Select the other Split View and pick Reverse Tabs, the tabs are reversed
    tabs.click_tab_by_index(3)
    split_view.expect_panel_url(SplitView.LEFT, URLS[2])
    split_view.expect_panel_url(SplitView.RIGHT, URLS[3])
    split_view.select_urlbar_menu_option(SplitView.REVERSE_TABS)
    split_view.expect_panel_url(SplitView.LEFT, URLS[3])
    split_view.expect_panel_url(SplitView.RIGHT, URLS[2])

    # Pick Close Both Tabs, both tabs of the Split View are closed
    split_view.select_urlbar_menu_option(SplitView.CLOSE_BOTH_TABS)
    split_view.expect_split_view_count(0)
    tabs.wait_for_num_tabs(len(URLS) - 2)
