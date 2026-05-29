import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

from modules.browser_object_navigation import Navigation
from modules.browser_object_tabbar import TabBar
from modules.page_object_generics import GenericPage

TEST_URL = "https://www.wikipedia.org/"
TEST_TEXT = "test"
SEARCH_FIELD = "search-field"


@pytest.fixture()
def test_case():
    return "134720"


@pytest.fixture()
def temp_selectors():
    return {
        SEARCH_FIELD: {
            "selectorData": "searchInput",
            "strategy": "id",
            "groups": [],
        }
    }


def _fill_search_field_and_verify(page: GenericPage):
    page.fill(SEARCH_FIELD, TEST_TEXT, press_enter=False)
    page.element_attribute_is(SEARCH_FIELD, "value", TEST_TEXT)
    return page.get_element(SEARCH_FIELD)


def _wait_for_reload_and_verify_empty_search_field(
    page: GenericPage,
    old_search_field,
):
    page.wait.until(EC.staleness_of(old_search_field))
    page.element_visible(SEARCH_FIELD)
    page.element_attribute_is(SEARCH_FIELD, "value", "")


def test_reload_tab_via_keyboard(
    driver: Firefox,
    sys_platform: str,
    temp_selectors,
):
    """
    C134720 - Verify that the opened tab can be reloaded via keyboard combinations
    """

    # Instantiate objects
    page = GenericPage(driver, url=TEST_URL)
    page.elements |= temp_selectors
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
    search_field = _fill_search_field_and_verify(page)

    # Step 3: Press the F5 button.
    tabbar.reload_tab(nav, extra_key=Keys.F5)
    _wait_for_reload_and_verify_empty_search_field(page, search_field)

    # Type text into the search field again so the second reload can be verified.
    search_field = _fill_search_field_and_verify(page)

    # Step 4: Hold the Ctrl/Cmd button and press the R button.
    tabbar.reload_tab(nav, mod_key=mod_key, extra_key="r")
    _wait_for_reload_and_verify_empty_search_field(page, search_field)
