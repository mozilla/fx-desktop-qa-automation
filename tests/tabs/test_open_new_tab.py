import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from modules.browser_object import TabBar


def test_open_new_tab_plus(driver: Firefox):
    # C134453
    tabs = TabBar(driver).open()
    tabs.new_tab_by_button()
    # add assert code

def test_open_new_tab_via_keyboard(driver: Firefox, sys_platform: str):
    # C134442
    tabs = TabBar(driver).open()
    tabs.NEW_TAB_KEY_COMBO[sys_platform]
    # add assert code
