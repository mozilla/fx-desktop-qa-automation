import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation

TEST_URL = "https://storage.googleapis.com/desktop_test_assets/TestCases/ScreenShare/ShareScreen.html"


@pytest.fixture()
def test_case():
    return "122534"


@pytest.fixture()
def temp_selectors():
    return {
        "start-capture": {
            "selectorData": "start",
            "strategy": "id",
            "groups": [],
        },
        "not-allowed": {"selectorData": "error", "strategy": "class", "groups": []},
    }


def test_deny_screen_capture(driver: Firefox, web_page):
    """
    C122534 - Verify that denying screen capture permissions prevents website from accessing the screen
    """
    # Instantiate Objects
    nav = Navigation(driver)
    page = web_page(TEST_URL)

    # Trigger the popup notification asking for camera permissions
    page.click_on("start-capture")

    # Block screen sharing for this website
    nav.element_clickable("popup-notification-secondary-button")
    nav.click_on("popup-notification-secondary-button")

    # Check that the website cannot access the screen
    page.element_has_text(
        "not-allowed",
        "Error: NotAllowedError: The request is not allowed by the user agent or the platform in the current context.",
    )
