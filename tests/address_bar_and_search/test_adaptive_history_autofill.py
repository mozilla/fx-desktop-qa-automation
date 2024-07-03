import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from modules.browser_object import Navigation
from modules.browser_object_tabbar import TabBar


@pytest.fixture()
def add_prefs():
    return [
        ("browser.search.region", "US"),
        ("browser.urlbar.autoFill.adaptiveHistory.enabled", True),
    ]


def test_add_adaptive_history_autofill(driver: Firefox):
    """
    C1814373 - Test to verify that typing the first three characters of a previously visited URL in the address bar
    triggers the adaptive history autofill.
    """

    nav = Navigation(driver).open()
    tabs = TabBar(driver)

    nav.search("https://news.google.com/home?hl=en-US&gl=US&ceid=US:en")
    WebDriverWait(driver, 10).until(
        lambda d: tabs.get_tab_title(tabs.get_tab(1)) == "Google News"
    )

    tabs.new_tab_by_button()
    tabs.wait_for_num_tabs(2)
    driver.switch_to.window(driver.window_handles[1])

    with driver.context(driver.CONTEXT_CHROME):
        x_icon = tabs.get_element("tab-x-icon", multiple=True)
        x_icon[0].click()

    # Type the first 3 characters of the visited URL in the address bar and select the suggested URL
    nav.type_in_awesome_bar("new")
    nav.get_element("firefox-suggest").click()
    nav.expect_in_content(
        EC.url_contains("https://news.google.com/home?hl=en-US&gl=US&ceid=US:en")
    )

    # Open a new tab, type the first 3 characters of the visited URL and see that it is autofilled directly
    tabs.new_tab_by_button()
    nav.type_in_awesome_bar("new")
    nav.expect_in_content(
        EC.url_contains("https://news.google.com/home?hl=en-US&gl=US&ceid=US:en")
    )
