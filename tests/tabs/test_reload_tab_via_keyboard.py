import platform

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from modules.browser_object_navigation import Navigation
from modules.page_object_generics import GenericPage
from modules.util import BrowserActions


@pytest.fixture()
def test_case():
    return "134720"


def test_reload_tab_via_keyboard(driver: Firefox, sys_platform: str):
    """
    C134720 - Verify F5 & Ctrl/Cmd+R will reload tab and clear the search field
    """

    test_url = "https://www.wikipedia.org/"
    test_text = "test"
    search_field_id = "searchInput"

    mod_key = Keys.COMMAND if platform.system() == "Darwin" else Keys.CONTROL

    # Open up Wikipedia Page
    page = GenericPage(driver, url=test_url).open()
    ba = BrowserActions(driver)
    wait = WebDriverWait(driver, 10)
    nav = Navigation(driver)

    # Type "test" into the search field
    search_field = wait.until(
        EC.visibility_of_element_located((By.ID, search_field_id))
    )
    search_field.click()
    ba.clear_and_fill(search_field, test_text, press_enter=False)
    assert search_field.get_attribute("value") == test_text

    # Perform Ctrl/Cmd+R from chrome context
    with driver.context(driver.CONTEXT_CHROME):
        nav.click_on("navigation-background-component")
        page.perform_key_combo(mod_key, "r")

    # Ensure page has reloaded and verify search field is empty
    wait.until(EC.staleness_of(search_field))
    search_field = wait.until(
        EC.visibility_of_element_located((By.ID, search_field_id))
    )
    assert search_field.get_attribute("value") == ""

    # Type "test" into the search field again
    search_field.click()
    ba.clear_and_fill(search_field, test_text, press_enter=False)
    assert search_field.get_attribute("value") == test_text

    # Perform F5 from chrome context
    with driver.context(driver.CONTEXT_CHROME):
        nav.click_on("navigation-background-component")
        page.perform_key_combo(Keys.F5)

    # Ensure page has reloaded and verify search field is empty
    wait.until(EC.staleness_of(search_field))  # ensure page reloaded
    search_field = wait.until(
        EC.visibility_of_element_located((By.ID, search_field_id))
    )
    assert search_field.get_attribute("value") == ""
