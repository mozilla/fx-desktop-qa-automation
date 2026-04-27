import platform

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from modules.browser_object_navigation import Navigation
from modules.browser_object_tabbar import TabBar
from modules.page_object_generics import GenericPage
from modules.util import BrowserActions

TEST_URL = "https://www.wikipedia.org/"
TEST_TEXT = "test"
SEARCH_FIELD_ID = "searchInput"


@pytest.fixture()
def test_case():
    return "134720"


def test_reload_tab_via_keyboard(driver: Firefox, sys_platform: str):
    """
    C134720 - Verify F5 & Ctrl/Cmd+R will reload tab and clear the search field
    """

    # Instantiate objects
    page = GenericPage(driver, url=TEST_URL)
    ba = BrowserActions(driver)
    nav = Navigation(driver)
    tabbar = TabBar(driver)

    mod_key = Keys.COMMAND if platform.system() == "Darwin" else Keys.CONTROL

    # Open up Wikipedia Page
    page.open()

    # Type "test" into the search field
    search_field = page.custom_wait(timeout=10).until(
        lambda d: driver.find_element(By.ID, SEARCH_FIELD_ID)
    )
    search_field = page.fill_field_and_verify(
        search_field, TEST_TEXT, ba.clear_and_fill
    )

    # Perform Ctrl/Cmd+R from chrome context
    tabbar.reload_tab(nav, mod_key=mod_key, extra_key="r")

    # Ensure page has reloaded and verify search field is empty
    search_field = page.wait_for_reload_and_verify_empty_field(
        search_field, SEARCH_FIELD_ID
    )

    # Type "test" into the search field again
    search_field = page.fill_field_and_verify(
        search_field, TEST_TEXT, ba.clear_and_fill
    )

    # Perform F5 from chrome context
    tabbar.reload_tab(nav, extra_key=Keys.F5)

    # Ensure page has reloaded and verify search field is empty
    page.wait_for_reload_and_verify_empty_field(search_field, SEARCH_FIELD_ID)
