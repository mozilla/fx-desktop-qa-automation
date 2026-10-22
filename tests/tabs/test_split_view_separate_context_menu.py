import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, SplitView, TabBar

# (URL, tab title) pairs, two per Split View
PAGES = [
    ("https://example.com/", "Example Domain"),
    ("https://www.wikipedia.org/", "Wikipedia"),
    ("https://www.youtube.com/", "YouTube"),
    ("https://www.facebook.com/", "Facebook"),
    ("https://www.python.org/", "Welcome to Python.org"),
    ("https://en.wikipedia.org/wiki/Firefox", "Firefox - Wikipedia"),
]
URLS = [url for url, _ in PAGES]
TITLES = [title for _, title in PAGES]
SPLIT_TO_SEPARATE = 1


@pytest.fixture()
def test_case():
    return "3903433"


@pytest.fixture()
def add_to_prefs_list():
    return [("browser.tabs.splitView.enabled", True)]


def test_split_view_separate_context_menu(driver: Firefox):
    """C3903433 - Verify that Split View can be separated using context menu."""

    tabs = TabBar(driver)
    context_menu = ContextMenu(driver)
    split_view = SplitView(driver)

    # Create 3 Split Views from pairs of tabs
    tabs.open_urls_in_tabs(URLS, open_first_in_current_tab=True)
    tabs.wait_for_num_tabs(len(URLS))
    for left, right in zip(TITLES[::2], TITLES[1::2]):
        split_view.create_split_view(left, right)
    all_tabs = [tabs.get_tab(index) for index in range(1, len(URLS) + 1)]
    split_view.expect(lambda _: split_view.count_tabs_in_split_view() == len(URLS))

    # Right-click a tab in one Split View and choose Separate Split View
    separated = all_tabs[SPLIT_TO_SEPARATE * 2 : SPLIT_TO_SEPARATE * 2 + 2]
    tabs.context_click(separated[0])
    context_menu.click_and_hide_menu("context-menu-separate-split-view")

    # Only that Split View's tabs are separated, the other Split Views stay
    still_split = [tab for tab in all_tabs if tab not in separated]
    split_view.expect(
        lambda _: split_view.get_elements("split-view-wrapper-tab") == still_split
    )

    # Both separated tabs stay open, in the same order
    tabs.wait_for_num_tabs(len(URLS))
    tabs.expect(lambda _: tabs.get_elements("all-tabs") == all_tabs)
