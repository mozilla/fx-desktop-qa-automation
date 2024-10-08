import pytest

from selenium.webdriver import Firefox
from modules.browser_object import Navigation
from modules.page_object_generics import GenericPage

import subprocess
import logging

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

TEST_URL = "https://mozilla.github.io/webrtc-landing/gum_test.html"


def test_camera_permissions_notification(driver: Firefox, temp_selectors, sys_platform):
    """
    C122536 - Verify that Camera only permission prompt is successfully displayed when the website asks for camera permissions
    """
    # Instatiate Objects
    nav = Navigation(driver)
    web_page = GenericPage(driver, url=TEST_URL).open()
    web_page.elements |= temp_selectors

    if sys_platform == "Windows":
        try:
            result = subprocess.run(['wmic', 'path', 'Win32_PnPEntity', 'where', 'Caption like "%camera%"', 'get', 'Caption'],
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output = result.stdout.decode()
            if "No Instance(s) Available" in output or not output.strip():
                    logging.warning("No cameras detected.")
            else:
                    logging.warning("Camera(s) detected:")
        except Exception as e:
            logging.warning(f"Error checking camera: {e}")

    # Trigger the popup notification asking for camera permissions
    web_page.click_on("camera-only")

    # Verify that the notification is displayed
    nav.element_attribute_contains("popup-notification", "label", "Allow ")
    nav.element_attribute_contains("popup-notification", "name", "mozilla.github.io")
    nav.element_attribute_contains("popup-notification", "endlabel", " to use your camera?")
    