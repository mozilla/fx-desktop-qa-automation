import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, Navigation, TabBar

TEST_URL = "https://youtube.com"
EXPECTED_ENGINE = "YouTube"


@pytest.fixture()
def test_case():
    return "3029002"


@pytest.fixture()
def hard_quit() -> bool:
    """Ensure Firefox quits cleanly after the test."""
    return True


def test_add_search_engine_from_address_bar(driver: Firefox):
    """
    C1365478 - Verify that OpenSearch engines can be added via the address bar context menu.
    """
    nav = Navigation(driver)
    menu = ContextMenu(driver)
    tabs = TabBar(driver)

    # Step 1: Open target site
    driver.get(TEST_URL)
    nav.custom_wait(timeout=25).until(lambda d: "youtube.com" in d.current_url)

    # Step 2: Open context menu on address bar and click "Add search engine"
    nav.context_click_in_awesome_bar()
    menu.click_context_item("context-menu-add-search-engine")

    # Step 3: A new tab should open with the engine config page, close it
    tabs.new_tab_by_button()
    youtube_tab = tabs.get_tab_by_title(EXPECTED_ENGINE)
    tabs.close_tab(youtube_tab)

    # Step 4: Open search mode switcher and verify engine is listed
    nav.click_on("searchmode-switcher")
    nav.element_exists("search-mode-switcher-option", labels=[EXPECTED_ENGINE])
    nav.click_on("searchmode-switcher")  # close dropdown
