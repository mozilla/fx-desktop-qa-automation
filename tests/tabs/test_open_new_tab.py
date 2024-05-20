import time

from selenium.webdriver import ActionChains, Firefox, Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from modules.browser_object import TabBar

def test_open_new_tab_plus(driver: Firefox):
    # C134453

    browser = TabBar(driver).open()
    driver.get("about:robots")
    browser.set_chrome_context()
    browser.new_tab_by_button()
    WebDriverWait(driver, 10).until(EC.title_contains("Mozilla Firefox"))
    assert driver.title == "Mozilla Firefox"

def test_open_new_tab_via_keyboard(driver: Firefox, sys_platform: str):
    # C134442

    browser = TabBar(driver).open()
    driver.get("about:robots")
    browser.set_chrome_context()
    # This action chain must be made into an object which accounts for cross
    # platform shortcut differences. As it is, will only work on macOS.
    ActionChains(driver).key_down(Keys.COMMAND).send_keys("t").key_up(Keys.CONTROL).perform()
    WebDriverWait(driver, 10).until(EC.title_contains("Mozilla Firefox"))
    assert driver.title == "Mozilla Firefox"
