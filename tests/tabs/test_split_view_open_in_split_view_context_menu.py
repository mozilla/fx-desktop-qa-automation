import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, SplitView, TabBar
from modules.page_object import ExamplePage, GenericPage

URLS = [
    "https://www.wikipedia.org/",
    "https://example.com/",
    "https://www.youtube.com/",
]
LINK_TAB = 2
LINK_URL = "https://www.iana.org/help/example-domains"
LINK_PAGE_LINK = "Domains"


@pytest.fixture()
def test_case():
    return "3903434"


@pytest.fixture()
def add_to_prefs_list():
    return [("browser.tabs.splitView.enabled", True)]


def test_split_view_open_in_split_view_context_menu(driver: Firefox):
    """
    C3903434 - Verify that Split View can be created when using the Open in Split View context menu option on a link
    """

    tabs = TabBar(driver)
    context_menu = ContextMenu(driver)
    split_view = SplitView(driver)
    example = ExamplePage(driver)
    link_page = GenericPage(driver)

    # Open the link tab between two other tabs
    tabs.open_urls_in_tabs(URLS, open_first_in_current_tab=True)
    tabs.wait_for_num_tabs(len(URLS))
    tabs_before_link = [tabs.get_tab(index) for index in range(1, len(URLS) + 1)]

    # Select the link tab and point the content context at it
    tabs.click_tab_by_index(LINK_TAB)
    driver.switch_to.window(driver.window_handles[LINK_TAB - 1])

    # Right-click the link
    example.scroll_to_element("learn-more")
    example.context_click("learn-more")

    # Choose Open in Split View
    context_menu.click_and_hide_menu("context-menu-open-link-in-split-view")

    # The link opens on the right, next to the tab
    split_view.expect_split_view_active()
    split_view.expect_panel_url(SplitView.LEFT, URLS[LINK_TAB - 1])
    split_view.expect_panel_url(SplitView.RIGHT, LINK_URL)
    assert split_view.count_tabs_in_split_view() == 2

    # The tab keeps its position, with the link tab right after it
    def _order_is_correct(_):
        all_tabs = tabs.get_elements("all-tabs")
        new_tabs = [tab for tab in all_tabs if tab not in tabs_before_link]
        return (
            all_tabs
            == tabs_before_link[:LINK_TAB] + new_tabs + tabs_before_link[LINK_TAB:]
        )

    tabs.expect(_order_is_correct)

    # Right-click a link in both views, Open in Split View is not shown
    for column, page, link, labels in [
        (SplitView.LEFT, example, "learn-more", None),
        (SplitView.RIGHT, link_page, "link-by-text", [LINK_PAGE_LINK]),
    ]:
        split_view.switch_to_panel(column)
        page.scroll_to_element(link, labels=labels)
        page.context_click(link, labels=labels)

        # The Split View item is hidden by default, so first confirm the menu opened
        context_menu.element_visible("context-menu-open-link-in-tab")
        context_menu.element_not_visible("context-menu-open-link-in-split-view")
        context_menu.hide_popup("contentAreaContextMenu")
