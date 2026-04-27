import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation
from modules.browser_object_tabbar import TabBar

TEST_URL = "https://www.nationalgeographic.com/science/"
EXPECTED_IN_TITLE = "Science"
TYPED_TEXT = "nat"
EXPECTED_TYPE = "autofill_adaptive"
EXPECTED_URL = "nationalgeographic.com/science"


@pytest.fixture()
def test_case():
    return "3029070"


@pytest.fixture()
def add_to_prefs_list():
    return [("browser.urlbar.autoFill.adaptiveHistory.enabled", True)]


def test_add_adaptive_history_autofill(driver: Firefox):
    """
    C1814373 - Verify adaptive history autofill triggers from address bar input.
    """
    # Instantiate objects
    nav = Navigation(driver)
    tabs = TabBar(driver)

    # Visit the test site and verify title
    nav.search(TEST_URL)
    tabs.expect_title_contains(EXPECTED_IN_TITLE)

    # Open new tab, close the original
    tabs.new_tab_by_button()
    driver.switch_to.window(driver.window_handles[1])
    tabs.close_first_tab_by_icon()

    # Type in address bar, then click adaptive suggestion
    nav.type_in_awesome_bar(TYPED_TEXT)
    nav.click_firefox_suggest()
    nav.url_contains(TEST_URL)

    # Open new tab and check for autofill suggestion
    tabs.new_tab_by_button()
    driver.switch_to.window(driver.window_handles[-1])
    nav.type_in_awesome_bar(TYPED_TEXT)
    nav.verify_autofill_adaptive_element(EXPECTED_TYPE, EXPECTED_URL)
