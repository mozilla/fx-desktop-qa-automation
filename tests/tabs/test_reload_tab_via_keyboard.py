import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

from modules.browser_object_navigation import Navigation
from modules.browser_object_tabbar import TabBar
from modules.page_object_generics import GenericPage

TEST_URL = "https://www.wikipedia.org/"
TEST_TEXT = "test"
SEARCH_FIELD = "wiki-search-bar"


@pytest.fixture()
def test_case():
    return "134720"


def test_reload_tab_via_keyboard(driver: Firefox, sys_platform: str):
    """
    C134720 - Verify that the opened tab can be reloaded via keyboard combinations
    """

    # Instantiate objects
    page = GenericPage(driver, url=TEST_URL)
    nav = Navigation(driver)
    tabbar = TabBar(driver)

    mod_key = Keys.COMMAND if sys_platform == "Darwin" else Keys.CONTROL

    # Step 1: Open a new tab.
    tabbar.new_tab_by_button()
    driver.switch_to.window(driver.window_handles[-1])

    # Step 2: Access any website.
    page.open()
    page.element_visible(SEARCH_FIELD)

    # Type text into the search field so the reload can be verified.
    page.fill_field_and_verify(SEARCH_FIELD, TEST_TEXT)

    # Step 3: Press the F5 button.
    previous_time_origin = page.get_page_time_origin()
    tabbar.reload_tab(nav, extra_key=Keys.F5)
    page.wait_for_reload_and_verify_empty_field(SEARCH_FIELD, previous_time_origin)

    # Type text into the search field again so the second reload can be verified.
    page.fill_field_and_verify(SEARCH_FIELD, TEST_TEXT)

    # Step 4: Hold the Ctrl/Cmd button and press the R button.
    previous_time_origin = page.get_page_time_origin()
    tabbar.reload_tab(nav, mod_key=mod_key, extra_key="r")
    page.wait_for_reload_and_verify_empty_field(SEARCH_FIELD, previous_time_origin)
