import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, ContextMenu, TabBar


@pytest.fixture()
def test_case():
    return "1365478"


@pytest.fixture()
def hard_quit():
    return True


def test_add_search_engine_from_address_bar(driver: Firefox):
    """
    C1365478 - Verify that Open Search engines can be added via the address bar context menu.
    """
    nav = Navigation(driver)
    menu = ContextMenu(driver)
    tabs = TabBar(driver)

    driver.get("https://youtube.com")
    nav.custom_wait(timeout=20).until(lambda d: "youtube.com" in d.current_url)

    with driver.context(driver.CONTEXT_CHROME):
        nav.context_click_in_awesome_bar()
        menu.click_context_item("context-menu-add-search-engine")

        tabs.new_tab_by_button()
        youtube_tab = tabs.get_tab_by_title("YouTube")
        tabs.close_tab(youtube_tab)

        nav.click_on("searchmode-switcher")
        nav.element_exists("search-mode-switcher-option", labels=["YouTube"])
        nav.click_on("searchmode-switcher")
