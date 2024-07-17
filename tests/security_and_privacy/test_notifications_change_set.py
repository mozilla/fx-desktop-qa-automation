import logging

import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutPrefs, GenericPage
from modules.util import BrowserActions, Utilities

NOTIFICATIONS_SITE = "https://www.bennish.net/web-notifications.html"
associated_labels = [
    ("notifications-allow-button", "Allow", "granted"),
    ("notifications-block-button", "Block", "denied"),
]


@pytest.fixture()
def add_prefs():
    return []


@pytest.mark.parametrize("button_data, button_text, permission", associated_labels)
def test_notifications_allow(
    driver: Firefox, button_data: str, button_text: str, permission: str
):
    """
    C159150: verifies that changing different settings allows for notifcations to be blocked
    """
    # instantiate objects
    ba = BrowserActions(driver)
    util = Utilities()
    alert_page = GenericPage(driver, url=NOTIFICATIONS_SITE).open()
    about_prefs = AboutPrefs(driver, category="privacy")

    alert_page.get_element("authorize-notifications-button").click()
    with driver.context(driver.CONTEXT_CHROME):
        about_prefs.get_element(button_data).click()

    check_notification_script = """
        return Notification.permission;
    """
    permission_status = driver.execute_script(check_notification_script)

    logging.info(f"Notification permission status: {permission_status}")
    assert permission_status == permission

    about_prefs.open()
    about_prefs.get_element("permissions-notifications-button").click()

    iframe = about_prefs.get_iframe()
    ba.switch_to_iframe_context(iframe)

    website_permissions = about_prefs.get_elements(
        "permissions-notifications-popup-websites"
    )
    assert len(website_permissions) == 1

    website_item = about_prefs.get_element(
        "permissions-notifications-popup-websites-item",
        labels=[util.get_domain_from_url(NOTIFICATIONS_SITE)],
    )

    notification_website_status = about_prefs.get_element(
        "permissions-notifications-popup-websites-item-status",
        parent_element=website_item,
    )
    assert notification_website_status.get_attribute("label") == button_text
