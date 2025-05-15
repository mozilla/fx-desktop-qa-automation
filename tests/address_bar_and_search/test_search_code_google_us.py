import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, Navigation, TabBar
from modules.page_object import ExamplePage


@pytest.fixture()
def test_case():
    return "3029765"


@pytest.fixture()
def add_to_prefs_list():
    return [("cookiebanners.service.mode", 1)]


FX_SEARCH_CODE = "client=firefox-b-1-d"
SEARCH_TERM = "soccer"


@pytest.mark.unstable(reason="Google re-captcha")
def test_search_code_google_us(driver: Firefox):
    """
    C1365268 - Default Search Code: Google - US
    This tests searching via Awesomebar and selected text
    """
    nav = Navigation(driver)
    context_menu = ContextMenu(driver)
    tab = TabBar(driver)
    example = ExamplePage(driver)

    def assert_search_code_in_url():
        assert FX_SEARCH_CODE in driver.current_url
        nav.clear_awesome_bar()

    # Search via the Awesomebar
    nav.search(SEARCH_TERM)
    tab.expect_title_contains("Google Search")
    assert_search_code_in_url()

    # Search via context menu of selected text
    example.search_selected_header_via_context_menu()

    context_menu.click_and_hide_menu("context-menu-search-selected-text")

    driver.switch_to.window(driver.window_handles[-1])
    tab.expect_title_contains("Google Search")
    assert_search_code_in_url()
