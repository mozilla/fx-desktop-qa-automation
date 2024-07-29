from time import sleep

import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.browser_object_tracker_panel import TrackerPanel
from modules.page_object_about_prefs import AboutPrefs

Tracker_URL = "https://senglehardt.com/test/trackingprotection/test_pages/tracking_protection.html"


@pytest.fixture()
def add_prefs():
    return [
        ("network.cookie.cookieBehavior", 0),
        ("privacy.trackingprotection.pbmode.enabled", False),
        ("privacy.trackingprotection.cryptomining.enabled", False),
        ("privacy.trackingprotection.fingerprinting.enabled", False),
        ("privacy.fingerprintingProtection.pbmode", False),
    ]


def test_blocked_tracking_content(driver: Firefox):
    """
    C446405.1: Ensure that ETP Custom mode with option Tracking Content -> In all windows set blocks tracking content
    """

    nav = Navigation(driver)
    tracker_panel = TrackerPanel(driver)
    about_prefs = AboutPrefs(driver, category="privacy").open()
    about_prefs.get_element("tracking-checkbox").click()
    about_prefs.get_element("tracking-in-all-windows").click()
    sleep(2)

    driver.get(Tracker_URL)
    nav.open_tracker_panel()

    driver.set_context(driver.CONTEXT_CHROME)

    tracker_panel.get_element("tracker-tracking-content").click()
    tracker_subview_title = tracker_panel.get_element("tracking-subview")
    assert tracker_subview_title.get_attribute("title") == "Tracking Content Blocked"


def test_allowed_tracking_content(driver: Firefox):
    """
    C446405.2: Ensure that ETP Custom mode with option Tracking Content -> Only in Private Windows set allows
    tracking content
    """

    nav = Navigation(driver)
    tracker_panel = TrackerPanel(driver)
    about_prefs = AboutPrefs(driver, category="privacy").open()
    about_prefs.get_element("tracking-checkbox").click()
    sleep(2)

    driver.get(Tracker_URL)
    nav.open_tracker_panel()

    driver.set_context(driver.CONTEXT_CHROME)

    tracker_panel.get_element("tracker-tracking-content").click()
    tracker_subview_title = tracker_panel.get_element("tracking-subview")
    assert (
        tracker_subview_title.get_attribute("title") == "Not Blocking Tracking Content"
    )
