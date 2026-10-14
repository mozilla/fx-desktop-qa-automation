import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation
from modules.page_object import GenericPage

TEST_URL = "https://joo.uber.space/frame-permissions.html"


@pytest.fixture()
def test_case():
    return "602565"


@pytest.fixture()
def temp_selectors():
    """Selectors for the test page, iframe picked by heading since allow lists repeat."""
    return {
        "permission-site-iframe": {
            "selectorData": "//h2[text()='https://permission.site with FP allowed']"
            "/following-sibling::iframe",
            "strategy": "xpath",
            "groups": ["doNotCache"],
        },
        "notifications-button": {
            "selectorData": "notifications",
            "strategy": "id",
            "groups": ["doNotCache"],
        },
        "persistent-storage-button": {
            "selectorData": "persistent-storage",
            "strategy": "id",
            "groups": ["doNotCache"],
        },
    }


def test_always_denied_permission(
    driver: Firefox, nav: Navigation, temp_selectors: dict
):
    """
    C602565 - Verify that some permissions are always denied
    """

    # Open the test page
    frame_permissions = GenericPage(driver, url=TEST_URL)
    frame_permissions.open()
    frame_permissions.elements |= temp_selectors
    nav.wait_for_page_to_load()

    # Request Notifications from the "FP allowed" permission.site iframe
    frame_permissions.switch_to_iframe_context(
        frame_permissions.get_element("permission-site-iframe")
    )
    frame_permissions.click_on("notifications-button")

    # "error" means not granted; confirm via the API that it is actually denied
    frame_permissions.element_attribute_contains(
        "notifications-button", "class", "error"
    )
    assert driver.execute_script("return Notification.permission;") == "denied", (
        "Notifications should be denied without prompting in a third-party iframe"
    )

    frame_permissions.click_on("persistent-storage-button")

    # "default" means navigator.storage.persist() resolved false, i.e. denied
    frame_permissions.element_attribute_contains(
        "persistent-storage-button", "class", "default"
    )

    # Neither request opened a permission doorhanger
    frame_permissions.switch_to_default_frame()
    nav.element_not_visible("popup-notification")
