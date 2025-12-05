import pytest
from selenium.webdriver import Firefox

from modules.browser_object_context_menu import ContextMenu
from modules.browser_object_navigation import Navigation
from modules.browser_object_tabbar import TabBar
from modules.page_object_generics import GenericPage
from modules.page_object_newtab import AboutNewtab


@pytest.fixture()
def test_case():
    return "3029117"


@pytest.fixture()
def add_to_prefs_list():
    return [("privacy.userContext.enabled", True)]


TOPSITE_TITLE = "Wikipedia"
TOPSITE_URL = "www.wikipedia.org"
EXPECTED_CONTAINER = "Work"


def test_open_link_in_new_container_tab(driver: Firefox) -> None:
    """
    C3029117 - Verify that a link opened from the context menu in a new container tab opens
    in the correct container and URL.
    """
    tabs = TabBar(driver)
    new_tab = AboutNewtab(driver)
    context_menu = ContextMenu(driver)
    nav = Navigation(driver)
    page = GenericPage(driver, url="about:newtab")

    # Open about:newtab and right-click to open context menu
    page.open()
    new_tab.open_topsite_context_menu_by_title(TOPSITE_TITLE)

    # Click first option and verify link opens in new tab
    context_menu.open_link_in_container()

    # Switch to new tab and verify URL and container
    tabs.switch_to_new_tab()
    nav.url_contains(TOPSITE_URL)
    nav.expect_container_label(EXPECTED_CONTAINER)
