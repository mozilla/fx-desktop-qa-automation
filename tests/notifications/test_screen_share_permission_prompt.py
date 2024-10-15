import pytest
from selenium.webdriver import Firefox
from modules.browser_object import Navigation
from modules.page_object_generics import GenericPage

@pytest.fixture()
def test_case():
    return "122532"

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

TEST_URL = "https://storage.googleapis.com/desktop_test_assets/TestCases/ScreenShare/ShareScreen.html"

def test_screen_share_permission_prompt(driver: Firefox, temp_selectors):
    """
    C122532 - Verify that the screen share permission prompt is successfully displayed
    """

    nav = Navigation(driver)
    web_page = GenericPage(driver, url=TEST_URL).open()
    web_page.elements |= temp_selectors

    # Step 1: Trigger the popup notification asking for screen sharing permissions
    web_page.click_on("start-capture")

    # Determine Screen Share permission prompt is successfully displayed
    assert nav.element_visible("popup-notification")
