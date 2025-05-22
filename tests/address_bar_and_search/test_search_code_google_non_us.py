import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.support.ui import WebDriverWait

from modules.browser_object import ContextMenu, Navigation, TabBar
from modules.page_object import ExamplePage

FX_SEARCH_CODE = "client%3Dfirefox-b-d"
SEARCH_TERM = "soccer"
EXPECTED_TITLE = "google.com"


@pytest.fixture()
def test_case():
    return "3029768"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.search.region", "DE"),
        ("cookiebanners.service.mode", 1),
    ]


def test_search_code_google_non_us(driver: Firefox):
    """
    C1365269 - Default Search Code: Google - non-US.
    Verifies the correct search code is applied for Awesomebar and selected text search.
    """
    nav = Navigation(driver)
    context_menu = ContextMenu(driver)
    tab = TabBar(driver)
    example = ExamplePage(driver)

    def verify_search_code_in_url():
        assert FX_SEARCH_CODE in driver.current_url, (
            f"Expected '{FX_SEARCH_CODE}' in URL, got: {driver.current_url}"
        )
        nav.clear_awesome_bar()

    # Search via Awesomebar
    nav.search(SEARCH_TERM)
    tab.expect_title_contains(EXPECTED_TITLE)
    verify_search_code_in_url()

    # Search via selected text context menu
    example.search_selected_header_via_context_menu()

    current_handles = driver.window_handles
    context_menu.click_and_hide_menu("context-menu-search-selected-text")

    WebDriverWait(driver, 10).until(
        lambda d: len(d.window_handles) > len(current_handles)
    )
    driver.switch_to.window(driver.window_handles[-1])
    tab.expect_title_contains(EXPECTED_TITLE)
    verify_search_code_in_url()
