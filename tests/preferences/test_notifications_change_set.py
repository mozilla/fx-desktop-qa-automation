import logging

import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutPrefs, GenericPage


@pytest.fixture()
def test_case():
    return "159150"


associated_labels = [
    ("notifications-allow-button", "Allow", "granted"),
    ("notifications-block-button", "Block", "denied"),
]


@pytest.fixture()
def about_prefs_category():
    return "privacy"


@pytest.fixture()
def test_url(driver):
    return "https://www.bennish.net/web-notifications.html"


@pytest.mark.parametrize("button_data, button_text, permission", associated_labels)
def test_notifications_allow(
    driver: Firefox,
    button_data: str,
    button_text: str,
    permission: str,
    about_prefs: AboutPrefs,
    test_url: str,
    generic_page: GenericPage,
):
    """
    C159150: verifies that changing different settings allows for notifications to be blocked
    """
    generic_page.open()

    generic_page.click_on("authorize-notifications-button")
    with driver.context(driver.CONTEXT_CHROME):
        about_prefs.get_element(button_data).click()

    check_notification_script = """
        return Notification.permission;
    """
    permission_status = driver.execute_script(check_notification_script)

    logging.info(f"Notification permission status: {permission_status}")
    assert permission_status == permission

    about_prefs.open()
    about_prefs.click_on("permissions-notifications-button")

    about_prefs.get_and_switch_iframe()

    website_permissions = about_prefs.get_elements(
        "permissions-notifications-popup-websites"
    )
    assert len(website_permissions) == 1

    about_prefs.element_attribute_is(
        "permissions-notifications-popup-websites-item-status", "label", button_text
    )
