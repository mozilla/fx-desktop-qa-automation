import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation
from modules.page_object_generics import GenericPage


@pytest.fixture()
def test_case():
    return "122534"


@pytest.fixture()
def temp_selectors():
    return {
        "start-capture": {
            "selectorData": 'start',
            "strategy": "id",
            "groups": [],
        }, 
        "not-allowed": {
            "selectorData": "error",
            "strategy": "class",
            "groups": []
        }
    }

TEST_URL = "https://storage.googleapis.com/desktop_test_assets/TestCases/ScreenShare/ShareScreen.html"


def test_deny_screen_capture(driver: Firefox, temp_selectors):
    """
    C122534 - Verify that denying screen capture permissions prevents website from accessing the screen
    """
    # Instatiate Objects
    nav = Navigation(driver)
    web_page = GenericPage(driver, url=TEST_URL).open()
    web_page.elements |= temp_selectors

    # Trigger the popup notification asking for camera permissions
    web_page.click_on("start-capture")

    # Block screen sharing for this website
    nav.element_clickable("popup-notification-block")
    nav.click_on("popup-notification-block")

    # Check that the website cannot access the screen
    web_page.element_has_text(
        "not-allowed", "Error: NotAllowedError: The request is not allowed by the user agent or the platform in the current context."
        )
    