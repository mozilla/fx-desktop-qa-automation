from time import sleep

import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.browser_object_tracker_panel import TrackerPanel
from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "446406"


SOCIAL_MEDIA_TRACKERS_URL = "https://senglehardt.com/test/trackingprotection/test_pages/social_tracking_protection.html"


@pytest.fixture()
def add_prefs():
    return [
        ("network.cookie.cookieBehavior", 0),
        ("privacy.trackingprotection.pbmode.enabled", False),
        ("privacy.trackingprotection.cryptomining.enabled", False),
        ("privacy.trackingprotection.fingerprinting.enabled", False),
        ("privacy.fingerprintingProtection.pbmode", False),
    ]


@pytest.mark.xfail  # blocked by bug 1866005
def test_blocking_social_media_trackers(driver: Firefox):
    """
    C446406: Ensure that ETP Custom mode with the option "Cross-site tracking cookies, and isolate other
    cross-site cookies" set in the Cookies section blocks social media trackers.
    """
    nav = Navigation(driver)
    tracker_panel = TrackerPanel(driver)
    about_prefs = AboutPrefs(driver, category="privacy").open()

    about_prefs.get_element("cookies-checkbox")
    about_prefs.get_element("cookies-isolate-social-media-option").click()
    sleep(3)

    driver.get(SOCIAL_MEDIA_TRACKERS_URL)
    nav.open_tracker_panel()

    driver.set_context(driver.CONTEXT_CHROME)

    tracker_panel.element_clickable("social-media-tracker-content")
    social_media_subview_title = tracker_panel.get_element("social-media-subview")
    assert (
        social_media_subview_title.get_attribute("title")
        == "Social Media Trackers Blocked"
    )
