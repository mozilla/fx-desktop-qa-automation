import logging
import subprocess

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
def set_prefs():
    """Set prefs"""
    return [("media.navigator.streams.fake", True)]


TEST_URL = "https://mozilla.github.io/webrtc-landing/gum_test.html"


def test_camera_permissions_notification(driver: Firefox, temp_selectors, sys_platform):
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
    nav.element_attribute_contains("popup-notification", "label", "Allow ")
    nav.element_attribute_contains("popup-notification", "name", "mozilla.github.io")
    nav.element_attribute_contains(
        "popup-notification", "endlabel", " to use your camera?"
    )
