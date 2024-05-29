from selenium.webdriver import Firefox
from selenium.webdriver.support import expected_conditions as EC

from modules.browser_object import TabBar


def test_open_new_tab_plus(driver: Firefox):
    """
    C134453 - A new tab can be opened from the dedicated button ("+")
    """
    browser = TabBar(driver).open()
    driver.get("about:robots")
    browser.set_chrome_context()
    browser.new_tab_by_button()
    browser.expect(EC.title_contains("Mozilla Firefox"))
    assert driver.title == "Mozilla Firefox"


def test_open_new_tab_via_keyboard(driver: Firefox, sys_platform: str):
    """
    C134442 - A new tab can be opened via keyboard combinations
    """
    browser = TabBar(driver).open()
    driver.get("about:robots")
    browser.set_chrome_context()
    browser.new_tab_by_keys(sys_platform)
    browser.expect(EC.title_contains("Mozilla Firefox"))
    assert driver.title == "Mozilla Firefox"
