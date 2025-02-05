import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.support import expected_conditions as EC

from modules.browser_object import Navigation, TabBar
from modules.browser_object_context_menu import ContextMenu


@pytest.fixture()
def test_case():
    return "1365478"


def test_add_search_engine_from_address_bar(driver: Firefox):
    """
    C1365478: Open Search Engines can be added using the address bar context click option.
    """
    nav = Navigation(driver)
    menu = ContextMenu(driver)
    tabs = TabBar(driver)

    # Visit the URL and wait until it is loaded
    driver.get("https://youtube.com")
    nav.custom_wait(timeout=20).until(EC.url_contains("www.youtube.com"))

    with driver.context(driver.CONTEXT_CHROME):
        # Right-Click the address bar and select the "Add YouTube" option
        nav.context_click_in_awesome_bar()
        menu.click_context_item("context-menu-add-search-engine")

        # Open a new tab and close the previous tab
        tabs.new_tab_by_button()
        previous_tab = tabs.get_tab_by_title("YouTube")
        tabs.close_tab(previous_tab)

        # Confirm that YouTube is an option in the search mode list
        nav.click_on("searchmode-switcher")
        nav.element_exists("search-mode-switcher-option", labels=["YouTube"])
        nav.click_on("searchmode-switcher")
