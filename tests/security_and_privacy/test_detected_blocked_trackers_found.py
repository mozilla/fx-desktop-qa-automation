from time import sleep

from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.page_object_about_prefs import AboutPrefs

def test_detected_blocked_trackers_found(driver: Firefox):
    """
    C446392: Ensure that the correct trackers are allowed and blocked
    """
    pass