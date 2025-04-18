import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from modules.browser_object import Navigation
from modules.browser_object_tabbar import TabBar

WAIT_TIMEOUT = 10
TEST_URL = "https://www.nationalgeographic.com/science/"
EXPECTED_TITLE = "Science"


@pytest.fixture()
def test_case():
    return "1814373"


@pytest.fixture()
def add_to_prefs_list():
    return [("browser.urlbar.autoFill.adaptiveHistory.enabled", True)]


def test_add_adaptive_history_autofill(driver: Firefox):
    """
    C1814373 - Verify adaptive history autofill triggers from address bar input.
    """
    nav = Navigation(driver)
    tabs = TabBar(driver)

    nav.search(TEST_URL)
    WebDriverWait(driver, WAIT_TIMEOUT).until(
        lambda d: tabs.get_tab_title(tabs.get_tab(1)) == EXPECTED_TITLE
    )

    tabs.new_tab_by_button()
    tabs.wait_for_num_tabs(2)
    driver.switch_to.window(driver.window_handles[1])

    with driver.context(driver.CONTEXT_CHROME):
        tabs.get_elements("tab-x-icon")[0].click()

    nav.type_in_awesome_bar("nat")
    with driver.context(driver.CONTEXT_CHROME):
        nav.get_element("firefox-suggest").click()

    nav.expect_in_content(EC.url_contains(TEST_URL))

    tabs.new_tab_by_button()
    tabs.wait_for_num_tabs(2)
    driver.switch_to.window(driver.window_handles[-1])
    nav.type_in_awesome_bar("nat")

    tabs.set_chrome_context()
    autofill_element = nav.get_element("search-result-autofill-adaptive-element")

    assert autofill_element.get_attribute("type") == "autofill_adaptive", (
        f"Expected type 'autofill_adaptive', got '{autofill_element.get_attribute('type')}'"
    )
    assert "nationalgeographic.com/science" in autofill_element.text, (
        f"Autofill text did not contain expected URL. Got: {autofill_element.text}"
    )
