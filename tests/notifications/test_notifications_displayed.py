from time import sleep

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation
from modules.page_object import GenericPage

PERMISSION_GRANTED_MSG = "Permission to display: granted"


@pytest.fixture()
def test_case():
    return "122443"


@pytest.fixture()
def temp_selectors():
    return {
        "authorize-button": {
            "selectorData": "button[onclick='notify.authorize()']",
            "strategy": "css",
            "groups": [],
        },
        "show-button": {
            "selectorData": "button[onclick='notify.show()']",
            "strategy": "css",
            "groups": [],
        },
        "console": {"selectorData": "console", "strategy": "id", "groups": []},
    }


def test_notifications_displayed(driver: Firefox, temp_selectors):
    bennish_test_page = GenericPage(
        driver, url="https://www.bennish.net/web-notifications.html"
    )
    bennish_test_page.open()
    bennish_test_page.elements |= temp_selectors
    nav = Navigation(driver)

    bennish_test_page.click_on("authorize-button")
    nav.click_on("popup-notification-primary-button")
    bennish_test_page.element_has_text("console", PERMISSION_GRANTED_MSG)
    bennish_test_page.click_on("show-button")
    sleep(3)
