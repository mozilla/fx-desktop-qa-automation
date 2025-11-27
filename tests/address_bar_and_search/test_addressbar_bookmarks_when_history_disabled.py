import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.browser_object_tabbar import TabBar
from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "3028908"


def test_addressbar_bookmarks_when_history_disabled(driver: Firefox):
    """
    C3028908 - Most relevant bookmarks are shown in the address bar even when history is disabled
    """

    # Instantiate objects
    nav = Navigation(driver)
    tabs = TabBar(driver)
    about_prefs = AboutPrefs(driver, category="search")

    # In addressbar press z and pick "Get Involved" page
    nav.type_verify_and_click("z", "Get Involved")

    # Repeat step from above
    tabs.new_tab_by_button()
    nav.type_verify_and_click("z", "Get Involved")

    # On z press check "Get Involved" page is shown as the first result
    tabs.new_tab_by_button()
    nav.type_in_awesome_bar("z")
    position = nav.verify_result_position("Get Involved")
    assert position == 1

    # Navigate to about:preferences and uncheck Browsing History
    tabs.new_tab_by_button()
    driver.switch_to.window(driver.window_handles[-1])
    about_prefs.open()
    about_prefs.uncheck_history_suggestion()

    # Open a new tab and press z
    tabs.new_tab_by_button()
    nav.type_in_awesome_bar("z")

    # Check "Get Involved" page is shown as the first result
    position = nav.verify_result_position("Get Involved")
    assert position == 1
