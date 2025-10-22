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


STATIC_CONTEXT_MENU_OPTIONS = {
    "context-menu-open-link-in-tab": "Open Link in New Tab",
    "context-menu-open-link-in-new-window": "Open Link in New Window",
    "context-menu-open-link-in-new-private-window": "Open Link in New Private Window",
    "context-menu-bookmark-link": "Bookmark Link",
    "context-menu-save-link": "Save Link As",
    "context-menu-copy-link": "Copy Link",
    "context-menu-inspect": "Inspect",
}

DYNAMIC_CONTEXT_MENU_ITEMS = ["context-menu-search-select"]

TOPSITE_TITLE = "Wikipedia"
TOPSITE_URL = "www.wikipedia.org"


def test_non_sponsored_topsite_context_menu_option(driver: Firefox) -> None:
    """
    C3029116 - Verifies that the browser's context menu displays the expected options
    when right-clicking a top site tile, and that the opened link matches the
    status panel URL shown on hover.
    """
    tabs = TabBar(driver)
    newtab = AboutNewtab(driver)
    context_menu = ContextMenu(driver)
    nav = Navigation(driver)
    page = GenericPage(driver, url="about:newtab")

    # Open about:newtab and hover over the topsite tite and verify status panel URL (bottom-left)
    page.open()
    title_element = newtab.get_topsite_element(TOPSITE_TITLE)
    newtab.hover(title_element)
    nav.verify_status_panel_url(TOPSITE_URL)
    status_panel_url = nav.get_status_panel_url()

    # Right-click to open context menu
    newtab.open_topsite_context_menu_by_title(TOPSITE_TITLE)

    # Verify context menu options
    context_menu.verify_topsites_tile_context_menu_options(
        STATIC_CONTEXT_MENU_OPTIONS,
        DYNAMIC_CONTEXT_MENU_ITEMS,
        TOPSITE_TITLE,
    )

    # Click first option and verify link opens in new tab
    context_menu.click_context_item("context-menu-open-link-in-tab")
    tabs.switch_to_new_tab()
    nav.url_contains(status_panel_url)
