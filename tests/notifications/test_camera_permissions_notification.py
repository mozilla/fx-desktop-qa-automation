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


# Test is unstable in MacOS GHA for now
def test_camera_permissions_notification(driver: Firefox, web_page):
    """
    C122536 - Verify that Camera only permission prompt is successfully displayed when the website asks for camera permissions
    """
    # Instantiate Objects
    nav = Navigation(driver)
    page = web_page(TEST_URL)

    # Trigger the popup notification asking for camera permissions
    page.click_on("camera-only")

    # Verify that the notification is displayed
    nav.expect_element_attribute_contains("popup-notification", "label", "Allow ")
    nav.expect_element_attribute_contains(
        "popup-notification", "name", "mozilla.github.io"
    )
    nav.expect_element_attribute_contains(
        "popup-notification", "endlabel", " to use your camera?"
    )

    nav.element_visible("popup-notification-secondary-button")
    nav.click_on("popup-notification-secondary-button")
