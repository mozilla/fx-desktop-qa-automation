import logging
from time import sleep

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation
from modules.page_object import GenericPage

PERMISSION_GRANTED_MSG = "Permission to display: granted"
MESSAGE_ONE_SHOWN = "Notification #1 showed"


@pytest.fixture()
def set_prefs():
    return [("dom.webnotifications.enabled", True)]


@pytest.fixture()
def test_case():
    return "122443"


@pytest.fixture()
def temp_selectors():
    return {
        "authorize-button": {
            "selectorData": "/html/body/div/p[4]/button[1]",
            "strategy": "xpath",
            "groups": [],
        },
        "show-button": {
            "selectorData": "/html/body/div/p[4]/button[2]",
            "strategy": "xpath",
            "groups": [],
        },
        "console": {"selectorData": "console", "strategy": "id", "groups": []},
    }


def test_notifications_displayed(
    driver: Firefox, temp_selectors, start_notification_listener
):
    bennish_test_page = GenericPage(
        driver, url="https://www.bennish.net/web-notifications.html"
    )
    bennish_test_page.open()
    bennish_test_page.elements |= temp_selectors
    nav = Navigation(driver)

    start_notification_listener()

    bennish_test_page.click_on("authorize-button")
    nav.click_on("popup-notification-primary-button")
    bennish_test_page.element_has_text("console", PERMISSION_GRANTED_MSG)
    bennish_test_page.click_on("show-button")
    bennish_test_page.element_has_text("console", MESSAGE_ONE_SHOWN)

    logging.info(driver.execute_script("return window.localStorage;"))
    logging.info(driver.execute_script("return window.notifications;"))
    # logging.info(bennish_test_page.get_localstorage_item("newestNotificationTitle"))
