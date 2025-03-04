from shutil import copyfile

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation
from modules.page_object import GenericPage

TEST_PHRASE = "Aloha"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [("dom.webnotifications.enabled", True)]


@pytest.fixture()
def test_case():
    return "122443"


@pytest.fixture()
def temp_page(tmp_path):
    loc = tmp_path / "notification_test.html"
    copyfile("data/notification_test.html", loc)
    return loc


@pytest.fixture()
def temp_selectors():
    return {
        "notification-text-input": {
            "selectorData": "notification-text",
            "strategy": "id",
            "groups": [],
        },
        "send-notification-button": {
            "selectorData": "send-notification-button",
            "strategy": "id",
            "groups": [],
        },
        "notification-log": {"selectorData": "log", "strategy": "id", "groups": []},
    }


@pytest.mark.ci
def test_notifications_displayed(driver: Firefox, temp_page, temp_selectors):
    """
    This test does not (and SHOULD not) test that the OS displays web notifications
    correctly. The only thing being examined is that the notification is sent.
    This is done by having our own test page where we know logging only happens
    after the send operation (should fail with an error before logging if failure)."""
    test_page = GenericPage(driver, url=f"file://{temp_page}")
    test_page.open()
    test_page.elements |= temp_selectors

    test_page.fill("notification-text-input", TEST_PHRASE, press_enter=False)

    test_page.click_on("send-notification-button")

    # All requests are logged with a message that contains the word 'permission'
    test_page.element_has_text("notification-log", "permission")

    # Grant permission if we need to
    if "requesting" in test_page.get_element("notification-log").text:
        nav = Navigation(driver)
        nav.click_on("popup-notification-primary-button")

    test_page.element_has_text("notification-log", TEST_PHRASE)
