import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from modules.browser_object import Navigation
from modules.browser_object_tabbar import TabBar


@pytest.fixture()
def add_prefs():
    return [
        ("browser.urlbar.autoFill.adaptiveHistory.enabled", True),
    ]


def test_add_adaptive_history_autofill(driver: Firefox):
    """
    C1814373 - Test to verify that typing the first three characters of a previously visited URL in the address bar
    triggers the adaptive history autofill.
    """

    nav = Navigation(driver).open()
    tabs = TabBar(driver)

    nav.search("https://www.nationalgeographic.com/science/")
    WebDriverWait(driver, 10).until(
        lambda d: tabs.get_tab_title(tabs.get_tab(1)) == "Science"
    )

    tabs.new_tab_by_button()
    tabs.wait_for_num_tabs(2)
    driver.switch_to.window(driver.window_handles[1])

    with driver.context(driver.CONTEXT_CHROME):
        x_icon = tabs.get_elements("tab-x-icon")
        x_icon[0].click()

    # Type the first 3 characters of the visited URL in the address bar and select the suggested URL
    nav.type_in_awesome_bar("nat")
    nav.get_element("firefox-suggest").click()
    nav.expect_in_content(
        EC.url_contains("https://www.nationalgeographic.com/science/")
    )

    tabs.set_content_context()

    # Open a new tab, type the first 3 characters of the visited URL
    tabs.new_tab_by_button()
    tabs.wait_for_num_tabs(2)
    driver.switch_to.window(driver.window_handles[-1])
    nav.type_in_awesome_bar("nat")

    autofill_adaptive_element = nav.get_element(
        "search-result-autofill-adaptive-element"
    )

    # Assertion to verify that the 'autofill_adaptive' type is found
    assert (
        autofill_adaptive_element.get_attribute("type") == "autofill_adaptive"
    ), f"Expected element type to be 'autofill_adaptive' but found '{autofill_adaptive_element.get_attribute('type')}'"

    # Assertion to check the autofilled URL is the expected one
    assert (
        "nationalgeographic.com/science" in autofill_adaptive_element.text
    ), "URL 'https://www.nationalgeographic.com/science' not found in autofill suggestions."
