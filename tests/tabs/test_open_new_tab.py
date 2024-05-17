import time

from selenium.webdriver import ActionChains, Firefox, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from modules.browser_object import TabBar

# def test_open_new_tab_plus(driver: Firefox):
# C134453
# tabs = TabBar(driver).open()
# tabs.new_tab_by_button()
# add assert code


def test_open_new_tab_via_keyboard(driver: Firefox, sys_platform: str):
    # C134442
    browser = TabBar(driver).open()
    driver.get("about:robots")
    browser.set_chrome_context()
    ActionChains(driver).key_down(Keys.COMMAND).send_keys("t").perform()
    WebDriverWait(driver, 10).until(EC.title_contains("New Tab"))
    assert driver.title == "New Tab"
    if driver.find_element(By.CLASS_NAME, "fake-editable"):
        print("We found the selector by CLASS_NAME")
    with driver.context(driver.CONTEXT_CONTENT):
        time.sleep(1)
    # add assert code
