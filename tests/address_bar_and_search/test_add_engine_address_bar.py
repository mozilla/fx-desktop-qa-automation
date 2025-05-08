import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, Navigation, TabBar

TEST_URL = "https://youtube.com"
EXPECTED_ENGINE = "YouTube"


@pytest.fixture()
def test_case():
    return "3029002"


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

    driver.get(TEST_URL)
    nav.custom_wait(timeout=20).until(lambda d: "youtube.com" in d.current_url)

    with driver.context(driver.CONTEXT_CHROME):
        nav.context_click_in_awesome_bar()
        menu.click_context_item("context-menu-add-search-engine")

        tabs.new_tab_by_button()
        youtube_tab = tabs.get_tab_by_title(EXPECTED_ENGINE)
        tabs.close_tab(youtube_tab)

        nav.click_on("searchmode-switcher")
        nav.element_exists("search-mode-switcher-option", labels=[EXPECTED_ENGINE])
        nav.click_on("searchmode-switcher")
