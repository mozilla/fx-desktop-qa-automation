from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation

NOTRACKERS_URL = "http://example.com/"


def test_no_trackers_detected(driver: Firefox):
    """
    C446391 No trackers are detected
    """
    # instantiate object and access url
    nav = Navigation(driver)
    driver.get(NOTRACKERS_URL)

    # Click on the shield icon and verify that trackers are detected
    with driver.context(driver.CONTEXT_CHROME):
        nav.get_element("shield-icon").click()
        assert nav.get_element("no-trackers-detected").is_displayed()
