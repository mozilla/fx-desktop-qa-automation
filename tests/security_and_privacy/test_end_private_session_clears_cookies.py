import pytest
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, PanelUi
from modules.page_object import GenericPage

URL = "https://senglehardt.com/test/dfpi/storage_access_api.html"
COOKIES_SET = "Cookies already set"
COOKIES_NOT_SET = "Cookies not yet set"


@pytest.fixture()
def test_case():
    return "2359319"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.privatebrowsing.resetPBM.enabled", True),
        ("browser.privatebrowsing.felt-privacy-v1", True),
    ]


def _wait_for_cookie_status(driver: Firefox, nav: Navigation, expected: str) -> None:
    """Wait for the cookie status in frame(0); skip if the external iframe never loads (flaky host)."""
    driver.switch_to.frame(0)
    try:
        nav.custom_wait(timeout=30).until(lambda d: expected in d.page_source)
    except TimeoutException:
        # A blank iframe means senglehardt.com did not serve its content; skip rather than fail
        if "cookie" not in driver.page_source.lower():
            pytest.skip("senglehardt.com iframe did not load (flaky external host)")
        raise


def test_end_private_session_clears_cookies(driver: Firefox):
    """
    C2359319 - Verify that via end a private session button cookies are cleared
    """
    # Instantiate objects
    nav = Navigation(driver)
    panel = PanelUi(driver)
    page = GenericPage(driver, url=URL)

    # Open a private window and switch to it
    panel.open_and_switch_to_new_window("private")

    # Open site
    page.open()

    # Refresh the page to make sure the cookie is set and stored
    nav.click_on("refresh-button")
    _wait_for_cookie_status(driver, nav, COOKIES_SET)

    # Click on the data clearance (End private session) button
    driver.switch_to.default_content()
    nav.end_private_session()
    driver.switch_to.window(driver.window_handles[-1])

    # Navigate back to the site and verify cookies are cleared
    page.open()
    _wait_for_cookie_status(driver, nav, COOKIES_NOT_SET)
