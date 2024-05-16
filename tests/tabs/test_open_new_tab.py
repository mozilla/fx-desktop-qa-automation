import time

import pytest
import logging
from selenium.webdriver import Firefox, ActionChains, Keys
from selenium.webdriver.common.by import By

from modules.browser_object import TabBar


# def test_open_new_tab_plus(driver: Firefox):
    # C134453
    # tabs = TabBar(driver).open()
    # tabs.new_tab_by_button()
    # add assert code

def test_open_new_tab_via_keyboard(driver: Firefox, sys_platform: str):
    # C134442
    TabBar(driver).open()
    with driver.context(driver.CONTEXT_CHROME):
        ActionChains(driver)\
            .key_down(Keys.COMMAND)\
            .send_keys("t")\
            .perform()
        time.sleep(1)
    with driver.context(driver.CONTEXT_CONTENT):
        time.sleep(1)
    # key_combo=tabs.NEW_TAB_KEY_COMBO[sys_platform]
    # print(key_combo)
    # logging.info(f"Key combo {key_combo}...")
    # add assert code
