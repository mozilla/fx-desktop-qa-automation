import sys
from os import environ
from time import sleep

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation
from modules.page_object_generics import GenericPage


@pytest.fixture()
def test_case():
    return "122536"


@pytest.fixture()
def temp_selectors():
    return {
        "camera-only": {
            "selectorData": 'input[type="button"][value="Camera"]',
            "strategy": "css",
            "groups": [],
        }
    }


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [("media.navigator.streams.fake", True)]


TEST_URL = "https://mozilla.github.io/webrtc-landing/gum_test.html"
MAC_GHA = environ.get("GITHUB_ACTIONS") == "true" and sys.platform.startswith("darwin")


@pytest.mark.skipif(MAC_GHA, reason="Test unstable in MacOS Github Actions")
def test_camera_permissions_notification(driver: Firefox, temp_selectors):
    """
    C122536 - Verify that Camera only permission prompt is successfully displayed when the website asks for camera permissions
    """
    # Instatiate Objects
    nav = Navigation(driver)
    web_page = GenericPage(driver, url=TEST_URL).open()
    web_page.elements |= temp_selectors

    # Trigger the popup notification asking for camera permissions
    web_page.click_on("camera-only")

    # Verify that the notification is displayed
    nav.expect_element_attribute_contains("popup-notification", "label", "Allow ")
    nav.expect_element_attribute_contains(
        "popup-notification", "name", "mozilla.github.io"
    )
    nav.expect_element_attribute_contains(
        "popup-notification", "endlabel", " to use your camera?"
    )

    sleep(1.5)
    nav.click_on("popup-notification-secondary-button")
