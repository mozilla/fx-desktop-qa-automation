import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, Navigation, SplitView, TabBar
from modules.page_object import ExamplePage

URLS = [
    "https://example.com/",
    "https://www.wikipedia.org/",
    "https://www.youtube.com/",
    "https://www.facebook.com/",
]
LEFT_TAB = "Example Domain"
RIGHT_TAB = "Wikipedia"
LINK_URL = "https://www.iana.org/help/example-domains"


@pytest.fixture()
def test_case():
    return "3903440"


@pytest.fixture()
def add_to_prefs_list():
    return [("browser.tabs.splitView.enabled", True)]


@pytest.mark.parametrize(
    "vertical_tabs", [False, True], ids=["horizontal_tabs", "vertical_tabs"]
)
def test_split_view_tab_link_correct_location(driver: Firefox, vertical_tabs: bool):
    """
    C3903440 - Verify that links opened from Split View in a new tab creates the new tabs in the correct location
    """

    tabs = TabBar(driver)
    context_menu = ContextMenu(driver)
    nav = Navigation(driver)
    split_view = SplitView(driver)
    example = ExamplePage(driver)

    # Use horizontal or vertical tabs for this parametrized case
    if vertical_tabs:
        nav.toggle_vertical_tabs()

    # Ensure that a Split View is created, containing tabs with links
    tabs.open_urls_in_tabs(URLS, open_first_in_current_tab=True)
    tabs.wait_for_num_tabs(len(URLS))
    split_view.create_split_view(LEFT_TAB, RIGHT_TAB)
    tabs_before_link = [tabs.get_tab(index) for index in range(1, len(URLS) + 1)]

    # Select the left view and open a link in a new tab using the context menu
    tabs.click_tab_by_title(LEFT_TAB)
    assert split_view.get_selected_column() == SplitView.LEFT
    split_view.switch_to_panel(SplitView.LEFT)
    example.scroll_to_element("learn-more")
    example.context_click("learn-more")
    context_menu.click_and_hide_menu("context-menu-open-link-in-tab")
    tabs.wait_for_num_tabs(len(URLS) + 1)

    # The link is opened right after the Split View: on its right side with
    # horizontal tabs, below it with vertical tabs
    split_view.expect_tab_next_to_split_view(LINK_URL, vertical=vertical_tabs)

    # The other tabs keep their places: the two Split View tabs come first, then
    # the new tab, then the rest
    def _order_is_correct(_):
        all_tabs = tabs.get_elements("all-tabs")
        new_tabs = [tab for tab in all_tabs if tab not in tabs_before_link]
        return all_tabs == tabs_before_link[:2] + new_tabs + tabs_before_link[2:]

    tabs.expect(_order_is_correct)
