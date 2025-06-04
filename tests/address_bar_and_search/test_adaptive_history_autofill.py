import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from modules.browser_object import Navigation
from modules.browser_object_tabbar import TabBar

WAIT_TIMEOUT = 10
TEST_URL = "https://www.nationalgeographic.com/science/"
EXPECTED_TITLE = "Science"
EXPECTED_TYPE = "autofill_adaptive"
EXPECTED_TEXT_FRAGMENT = "nationalgeographic.com/science"


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
    from dotenv import load_dotenv

    load_dotenv()
    nav = Navigation(driver)
    tabs = TabBar(driver)

    # Step 1: Visit the test site and verify tab title
    nav.search(TEST_URL)
    WebDriverWait(driver, WAIT_TIMEOUT).until(
        lambda d: tabs.get_tab_title(tabs.get_tab(1)) == EXPECTED_TITLE
    )

    # Step 2: Open new tab, close the original
    tabs.new_tab_by_button()
    tabs.wait_for_num_tabs(2)
    driver.switch_to.window(driver.window_handles[1])
    tabs.close_first_tab_by_icon()

    # Step 3: Type in address bar, click adaptive suggestion
    nav.type_in_awesome_bar("nat")
    nav.click_firefox_suggest()
    nav.expect_in_content(EC.url_contains(TEST_URL))

    # Step 4: Open new tab and check for autofill suggestion
    tabs.new_tab_by_button()
    tabs.wait_for_num_tabs(2)
    driver.switch_to.window(driver.window_handles[-1])
    nav.type_in_awesome_bar("nat")

    tabs.set_chrome_context()
    autofill_element = nav.get_element("search-result-autofill-adaptive-element")

    assert autofill_element.get_attribute("type") == EXPECTED_TYPE, (
        f"Expected type '{EXPECTED_TYPE}', got '{autofill_element.get_attribute('type')}'"
    )
    assert EXPECTED_TEXT_FRAGMENT in autofill_element.text, (
        f"Autofill text did not contain expected URL. Got: {autofill_element.text}"
    )
