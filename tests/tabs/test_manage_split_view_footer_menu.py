import pytest
from selenium.webdriver import Firefox

from modules.browser_object import SplitView, TabBar

URLS = [
    "https://example.com/",
    "https://www.wikipedia.org/",
    "https://www.youtube.com/",
    "https://www.facebook.com/",
]
FIRST_SPLIT = ("Example Domain", "Wikipedia")
SECOND_SPLIT = ("YouTube", "Facebook")


@pytest.fixture()
def test_case():
    return "3903446"


@pytest.fixture()
def add_to_prefs_list():
    return [("browser.tabs.splitView.enabled", True)]


def test_manage_split_view_footer_menu(driver: Firefox):
    """
    C3903446 - Verify that Split View can be managed using the three-dot footer menu inside the Split View tab
    """

    tabs = TabBar(driver)
    split_view = SplitView(driver)

    # Ensure multiple Split Views are created
    tabs.open_urls_in_tabs(URLS, open_first_in_current_tab=True)
    tabs.wait_for_num_tabs(len(URLS))
    split_view.create_split_view(*FIRST_SPLIT)
    split_view.create_split_view(*SECOND_SPLIT)
    split_view.expect(lambda _: split_view.count_tabs_in_split_view() == 4)

    # Select one Split View and pick Separate Tabs from the footer menu, it is
    # broken up while both tabs stay open
    tabs.click_tab_by_title(FIRST_SPLIT[0])
    split_view.expect_split_view_active()
    split_view.select_footer_menu_option(SplitView.SEPARATE_TABS)
    split_view.expect_split_view_active(False)
    split_view.expect(lambda _: split_view.count_tabs_in_split_view() == 2)
    tabs.wait_for_num_tabs(len(URLS))

    # Select the other Split View and pick Reverse Tabs, its tabs swap sides
    tabs.click_tab_by_title(SECOND_SPLIT[0])
    split_view.expect_split_view_active()
    split_view.expect_panel_url_contains(SplitView.LEFT, "youtube.com")
    split_view.expect_panel_url_contains(SplitView.RIGHT, "facebook.com")
    split_view.select_footer_menu_option(SplitView.REVERSE_TABS)
    split_view.expect_panel_url_contains(SplitView.LEFT, "facebook.com")
    split_view.expect_panel_url_contains(SplitView.RIGHT, "youtube.com")

    # Pick Close Both Tabs, both tabs of the Split View are closed
    split_view.select_footer_menu_option(SplitView.CLOSE_BOTH_TABS)
    tabs.wait_for_num_tabs(len(URLS) - 2)
    split_view.expect(lambda _: split_view.count_tabs_in_split_view() == 0)
    split_view.expect_split_view_active(False)
