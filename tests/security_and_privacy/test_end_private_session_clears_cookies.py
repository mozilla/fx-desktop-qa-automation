import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, PanelUi
from modules.page_object import GenericPage


@pytest.fixture()
def test_case():
    return "2359319"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.privatebrowsing.resetPBM.enabled", True),
        ("browser.privatebrowsing.felt-privacy-v1", True),
    ]


URL = "https://senglehardt.com/test/dfpi/storage_access_api.html"


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
    driver.switch_to.frame(0)
    nav.wait.until(lambda d: "Cookies already set" in d.page_source)
    assert "Cookies already set" in driver.page_source

    # Click on the data clearance (End private session) button
    driver.switch_to.default_content()
    nav.end_private_session()
    driver.switch_to.window(driver.window_handles[-1])

    # Navigate back to the site and verify cookies are cleared
    page.open()
    driver.switch_to.frame(0)
    nav.wait.until(lambda d: "Cookies not yet set" in d.page_source)
    assert "Cookies not yet set" in driver.page_source
