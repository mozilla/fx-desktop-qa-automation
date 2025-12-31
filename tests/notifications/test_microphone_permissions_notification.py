from time import sleep

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation
from modules.page_object_generics import GenericPage


@pytest.fixture()
def test_case():
    return "122539"


@pytest.fixture()
def temp_selectors():
    return {
        "microphone-only": {
            "selectorData": 'input[type="button"][value="Microphone"]',
            "strategy": "css",
            "groups": [],
        }
    }


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [("media.navigator.streams.fake", True)]


TEST_URL = "https://mozilla.github.io/webrtc-landing/gum_test.html"


def _verify_microphone_permission_prompt(driver: Firefox, nav: Navigation) -> None:
    """
    Verifies the microphone permission prompt is visible and contains expected copy/host.
    """
    nav.element_visible("popup-notification")
    nav.expect_element_attribute_contains("popup-notification", "label", "Allow ")
    nav.expect_element_attribute_contains(
        "popup-notification", "name", "mozilla.github.io"
    )
    nav.expect_element_attribute_contains(
        "popup-notification", "endlabel", " to use your microphone?"
    )


# Test is unstable in MacOS GHA for now
def test_microphone_permissions_notification(driver: Firefox, temp_selectors):
    """
    C122539 - Verify that Microphone only permission prompt is successfully displayed when the website asks for microphone permissions
    """
    # Instatiate Objects
    nav = Navigation(driver)
    web_page = GenericPage(driver, url=TEST_URL).open()
    web_page.elements |= temp_selectors

    # Trigger the popup notification asking for camera permissions
    web_page.click_on("microphone-only")

    # Verify that the notification is displayed
    _verify_microphone_permission_prompt(driver, nav)

    nav.click_on("popup-notification-secondary-button")
