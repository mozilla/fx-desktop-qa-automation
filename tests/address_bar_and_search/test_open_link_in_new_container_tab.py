import time

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
    C3029117 -
    """
    tabs = TabBar(driver)
    newtab = AboutNewtab(driver)
    context_menu = ContextMenu(driver)
    nav = Navigation(driver)
    page = GenericPage(driver, url="about:newtab")

    # Open about:newtab and hover over the desired TOPSITE_TITLE tile and verify status panel URL (bottom-left)
    page.open()

    # Right-click to open context menu
    newtab.open_topsite_context_menu_by_title(TOPSITE_TITLE)

    # Click first option and verify link opens in new tab
    context_menu.click_context_item("context-menu-open-link-in-new_container_tab")
    context_menu.click_on("context-menu-open-link-in-container-work")
    tabs.switch_to_new_tab()
    nav.url_contains(TOPSITE_URL)
    nav.set_chrome_context()
    assert nav.get_element("userContext-label").text == EXPECTED_CONTAINER
    # time.sleep(10)
