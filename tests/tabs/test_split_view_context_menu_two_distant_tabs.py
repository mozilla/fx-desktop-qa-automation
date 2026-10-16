import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, SplitView, TabBar

URLS = [
    "https://example.com/",
    "https://www.wikipedia.org/",
    "https://www.youtube.com/",
    "https://www.facebook.com/",
]
ACTIVE_TAB = 1
DISTANT_TAB = 4
ACTIVE_URL = URLS[ACTIVE_TAB - 1]
DISTANT_URL = URLS[DISTANT_TAB - 1]


@pytest.fixture()
def test_case():
    return "3903435"


@pytest.fixture()
def add_to_prefs_list():
    return [("browser.tabs.splitView.enabled", True)]


def test_split_view_context_menu_two_distant_tabs(driver: Firefox, sys_platform: str):
    """
    C3903435 - Verify that a Split View is successfully created using the context menu when two distant tabs are selected
    """

    tabs = TabBar(driver)
    context_menu = ContextMenu(driver)
    split_view = SplitView(driver)

    # Ensure that multiple tabs are opened
    tabs.open_urls_in_tabs(URLS, open_first_in_current_tab=True)
    tabs.wait_for_num_tabs(len(URLS))

    # Focus a tab and multi-select a distant tab, then right-click one of them
    # and use the Open in Split View option
    selected_tabs = tabs.select_multiple_tabs_by_indices(
        [ACTIVE_TAB, DISTANT_TAB], sys_platform
    )
    tabs.context_click(selected_tabs[1])
    context_menu.element_attribute_contains(
        "context-menu-add-split-view", "label", "Open in Split View"
    )
    context_menu.click_and_hide_menu("context-menu-add-split-view")

    # The Split View is created with the active tab on the left side
    split_view.expect_split_view_active()
    split_view.expect_panel_url(SplitView.LEFT, ACTIVE_URL)
    split_view.expect_panel_url(SplitView.RIGHT, DISTANT_URL)
    assert split_view.count_tabs_in_split_view() == 2

    # The distant tab is brought next to the active tab in the tab strip
    expected_order = [ACTIVE_URL, DISTANT_URL, URLS[1], URLS[2]]
    tabs.expect(lambda _: tabs.get_tab_urls_in_order() == expected_order)
