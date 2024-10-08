import pytest

from selenium.webdriver import Firefox
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

TEST_URL = "https://mozilla.github.io/webrtc-landing/gum_test.html"


def test_camera_permissions_notification(driver: Firefox, temp_selectors):
    """
    C122536 - Verify that Camera only permission prompt is successfully displayed when the website asks for camera permissions
    """
    # Instatiate Objects
    web_page = GenericPage(driver, url=TEST_URL).open()
    web_page.elements |= temp_selectors

    # Trigger the popup notification asking for camera permissions
    web_page.click_on("camera-only")

    # Verify that the notification is displayed
    with driver.context(driver.CONTEXT_CHROME):
        popup_notification = web_page.get_element("popup-notification")
        assert popup_notification.get_attribute("label") == "Allow "
        assert popup_notification.get_attribute("name") == "mozilla.github.io"
        assert popup_notification.get_attribute("endlabel") == " to use your camera?"
    