import pytest
from selenium.webdriver import Firefox

from modules.browser_object_context_menu import ContextMenu
from modules.browser_object_navigation import Navigation
from modules.browser_object_tabbar import TabBar
from modules.page_object_generics import GenericPage
from modules.page_object_newtab import AboutNewtab


@pytest.fixture()
def test_case():
    return "3029116"


EXPECTED_CONTEXT_MENU_OPTIONS = {
    "context-menu-open-link-in-tab": "Open Link in New Tab",
    "context-menu-open-link-in-new-window": "Open Link in New Window",
    "context-menu-open-link-in-new-private-window": "Open Link in New Private Window",
    "context-menu-bookmark-link": "Bookmark Link",
    "context-menu-save-link": "Save Link As...",
    "context-menu-copy-link": "Copy Link",
    "context-menu-search-select": "Search Google for",
    "context-menu-ask-chatbot": "Ask an AI Chatbot",
    "context-menu-inspect": "Inspect",
}

TOPSITE_TITLE = "Wikipedia"


def test_non_sponsored_topsite_context_menu_option(driver: Firefox) -> None:
    """
    C3029116 - Verifies that the browser's context menu displays the expected options
    when right-clicking a top site tile, and that the opened link matches the
    status panel URL shown on hover.
    """
    # Instantiate page objects
    tabs = TabBar(driver)
    newtab = AboutNewtab(driver)
    context_menu = ContextMenu(driver)
    nav = Navigation(driver)
    page = GenericPage(driver, url="about:newtab")

    # Hover over Wikipedia tile and capture the status panel URL (browser's bottom-left corner)
    page.open()
    newtab.hover_topsite_and_verify_url(TOPSITE_TITLE, "wikipedia.org")
    status_panel_url = nav.get_status_panel_url()

    # Right-click on the Wikipedia tile to open context menu
    newtab.open_topsite_context_menu_by_title(TOPSITE_TITLE)

    # Verify all expected context menu options are present
    for selector, description in EXPECTED_CONTEXT_MENU_OPTIONS.items():
        context_menu.element_visible(selector)

    # Click "Open Link in New Tab" from context menu
    context_menu.click_context_item("context-menu-open-link-in-tab")

    # Switch to the newly opened tab
    tabs.switch_to_new_tab()
    nav.url_contains(status_panel_url)
