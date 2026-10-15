import pytest
from selenium.webdriver import Firefox

from modules.browser_object import SplitView, TabBar

URLS = ["https://example.com/", "https://www.wikipedia.org/"]
SECOND_SPLIT_TAB = "Wikipedia"


@pytest.fixture()
def test_case():
    return "3903441"


@pytest.fixture()
def add_to_prefs_list():
    return [("browser.tabs.splitView.enabled", True)]


def test_dissolve_split_view_on_tab_close(driver: Firefox):
    """
    C3903441 - Verify that Split View can be dissolved when closing one of the tabs
    """

    tabs = TabBar(driver)
    split_view = SplitView(driver)

    # Ensure that at least one Split View is created
    tabs.open_urls_in_tabs(URLS, open_first_in_current_tab=True)
    tabs.wait_for_num_tabs(len(URLS))
    split_view.create_split_view(1, SECOND_SPLIT_TAB)
    split_view.expect_panel_url(SplitView.LEFT, URLS[0])
    split_view.expect_panel_url_contains(SplitView.RIGHT, "wikipedia.org")
    assert split_view.count_tabs_in_split_view() == 2

    # Close one of the tabs inside the Split View by clicking the X button
    tabs.close_tab(tabs.get_tab(SECOND_SPLIT_TAB))

    # The Split View is dissolved, and only the remaining tab remains open
    tabs.wait_for_num_tabs(1)
    split_view.expect_split_view_active(False)
    assert split_view.count_tabs_in_split_view() == 0
    driver.switch_to.window(driver.window_handles[0])
    assert driver.current_url == URLS[0]
