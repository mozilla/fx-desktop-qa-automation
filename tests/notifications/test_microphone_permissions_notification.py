import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation


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
    nav.element_attribute_contains("popup-notification", "label", "Allow ")
    nav.element_attribute_contains("popup-notification", "name", "mozilla.github.io")
    nav.element_attribute_contains(
        "popup-notification", "endlabel", " to use your microphone?"
    )


# Test is unstable in MacOS GHA for now
def test_microphone_permissions_notification(driver: Firefox, web_page):
    """
    C122539 - Verify that Microphone only permission prompt is successfully displayed when the website asks for microphone permissions
    """
    # Instantiate Objects
    nav = Navigation(driver)
    page = web_page(TEST_URL)

    # Trigger the popup notification asking for camera permissions
    page.click_on("microphone-only")

    # Verify that the notification is displayed
    _verify_microphone_permission_prompt(driver, nav)

    nav.click_on("popup-notification-secondary-button")
