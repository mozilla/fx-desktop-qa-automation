from shutil import copyfile

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, PanelUi
from modules.page_object import GenericPage

COOKIE_TEST_PAGE = "cookie_test.html"


@pytest.fixture()
def test_case():
    return "2359319"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.privatebrowsing.resetPBM.enabled", True),
        ("browser.privatebrowsing.felt-privacy-v1", True),
    ]


@pytest.fixture()
def temp_page(tmp_path):
    loc = tmp_path / COOKIE_TEST_PAGE
    copyfile(f"data/pages/{COOKIE_TEST_PAGE}", loc)
    return loc


def test_end_private_session_clears_cookies(driver: Firefox, temp_page):
    """
    C2359319 - Verify that via end a private session button cookies are cleared
    """
    # Instantiate objects
    nav = Navigation(driver)
    panel = PanelUi(driver)
    page = GenericPage(driver, url=f"file://{temp_page}")

    # Open a private window and switch to it
    panel.open_and_switch_to_new_window("private")

    # Open site; the first visit sets the cookie
    page.open()

    # Refresh the page to make sure the cookie is set and stored
    nav.click_on("refresh-button")
    nav.wait.until(lambda d: "Cookies already set" in d.page_source)

    # Click on the data clearance (End private session) button
    nav.end_private_session()
    driver.switch_to.window(driver.window_handles[-1])

    # Navigate back to the site and verify cookies are cleared
    page.open()
    nav.wait.until(lambda d: "Cookies not yet set" in d.page_source)
