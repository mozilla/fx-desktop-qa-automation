from time import sleep

from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation

CRYPTOMINERS_URL = "https://senglehardt.com/test/trackingprotection/test_pages/fingerprinting_and_cryptomining.html"


def test_cryptominers_blocked_and_shown_in_info_panel(driver: Firefox):
    """
    C450232: Cryptominers are blocked and shown in Standard mode in the Information pannel
    """
    # Access URL, needed sleep otherwise cryptomining will be displayed as unblocked
    nav = Navigation(driver)
    sleep(4)
    driver.get(CRYPTOMINERS_URL)

    # Click on the shield icon and verify that cryptominers are blocked
    with driver.context(driver.CONTEXT_CHROME):
        nav.get_element("shield-icon").click()
        assert nav.get_element("cryptominers").is_displayed()
