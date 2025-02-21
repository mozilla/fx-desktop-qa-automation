import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.support.wait import WebDriverWait

from modules.browser_object import Navigation, PanelUi
from modules.page_object import AboutPrefs


@pytest.fixture()
def test_case():
    return "1362731"


HTTP_SITE = "http://example.com"


def test_https_first_mode_in_private_browsing(driver: Firefox):
    """
    C1362731 Check that https First Mode is properly enabled and working in Private Browsing
    """

    # Navigate to the HTTP Site in a Private Window
    prefs = AboutPrefs(driver, category="privacy")
    prefs.open()
    prefs.select_https_only_setting(prefs.HTTPS_ONLY_STATUS.HTTPS_ONLY_PRIVATE)
    hamburger = PanelUi(driver)
    hamburger.open_private_window()

    # nav = Navigation(driver)
    # nav.switch_to_new_window()

    # Using this instead of switch_to_new_window, suspect that may be unstable
    # on Linux CI machines. (slow to actually fully load the new Window)
    non_private_window = driver.current_window_handle
    original_window_idx = driver.window_handles.index(non_private_window)
    private_window = driver.window_handles[1 - original_window_idx]
    driver.switch_to.window(private_window)
    driver.get(HTTP_SITE)

    # Wait for the URL to be redirected to HTTPS
    assert WebDriverWait(driver, 10).until(
        lambda d: d.current_url.startswith("https://"),
        message=f"Final URL should use HTTPS, but was: {driver.current_url}",
    )
