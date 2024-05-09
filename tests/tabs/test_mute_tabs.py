from selenium.webdriver import Firefox

from modules.browser_object import Navigation


def test_mute_tab(driver: Firefox):
    nav = Navigation(driver).open()
    driver.get("https://mozilla.com")
