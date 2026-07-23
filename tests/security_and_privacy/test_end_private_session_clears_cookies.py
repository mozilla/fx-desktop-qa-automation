from shutil import copyfile

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, PanelUi
from modules.page_object import GenericPage

SENGLEHARDT_URL = "https://senglehardt.com/test/dfpi/storage_access_api.html"
COOKIE_TEST_PAGE = "cookie_test.html"
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


@pytest.fixture()
def temp_page(tmp_path):
    loc = tmp_path / COOKIE_TEST_PAGE
    copyfile(f"data/pages/{COOKIE_TEST_PAGE}", loc)
    return loc


def test_end_private_session_clears_cookies(
    driver: Firefox, sys_platform: str, temp_page
):
    """
    C2359319 - Verify that via end a private session button cookies are cleared
    """
    # Instantiate objects
    nav = Navigation(driver)
    panel = PanelUi(driver)

    # Windows renders the external DFPI page's first iframe blank in CI; use a local storage page there
    on_windows = sys_platform == "Windows"
    url = f"file://{temp_page}" if on_windows else SENGLEHARDT_URL
    page = GenericPage(driver, url=url)

    # Open a private window and switch to it
    panel.open_and_switch_to_new_window("private")

    # Open site; the first visit stores the data
    page.open()

    # Refresh the page to make sure the data is set and stored
    nav.click_on("refresh-button")
    if not on_windows:
        driver.switch_to.frame(0)
    nav.wait.until(lambda d: COOKIES_SET in d.page_source)

    # Click on the data clearance (End private session) button
    if not on_windows:
        driver.switch_to.default_content()
    nav.end_private_session()
    driver.switch_to.window(driver.window_handles[-1])

    # Navigate back to the site and verify the data is cleared
    page.open()
    if not on_windows:
        driver.switch_to.frame(0)
    nav.wait.until(lambda d: COOKIES_NOT_SET in d.page_source)
