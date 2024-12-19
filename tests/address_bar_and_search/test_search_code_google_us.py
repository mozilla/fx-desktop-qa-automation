import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from modules.browser_object import ContextMenu, Navigation, TabBar
from modules.page_object import ExamplePage


@pytest.fixture()
def test_case():
    return "1365268"


# Set constant
FX_SEARCH_CODE = "client=firefox-b-1-d"


def test_search_code_google_us(driver: Firefox):
    """
    C1365268 - Default Search Code: Google - US
    This tests searching via Awesomebar and selected text
    """

    # Create objects
    nav = Navigation(driver)
    context_menu = ContextMenu(driver)
    tab = TabBar(driver)
    example = ExamplePage(driver)

    def search_code_assert():
        # Function to check the search code of a Google search in US region
        search_url = driver.current_url
        assert FX_SEARCH_CODE in search_url
        nav.clear_awesome_bar()

    # Check code generated from the Awesome bar search
    nav.search("soccer")
    tab.expect_title_contains("Google Search")
    search_code_assert()

    # Check code generated from the context click of selected text
    with driver.context(driver.CONTEXT_CONTENT):
        example.open()
        h1_tag = (By.TAG_NAME, "h1")
        example.triple_click(h1_tag)
        example.context_click(h1_tag)
    context_menu.click_and_hide_menu("context-menu-search-selected-text")

    # Switch to the newly opened tab and run the code check
    window_handles = driver.window_handles
    driver.switch_to.window(window_handles[-1])
    tab.expect_title_contains("Google Search")
    search_code_assert()
