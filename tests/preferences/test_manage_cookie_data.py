import logging
from time import sleep

import pytest
from selenium.webdriver import Firefox

from modules.page_object_prefs import AboutPrefs
from modules.util import BrowserActions


@pytest.fixture()
def test_case():
    return "143633"


COOKIE_SITE = "google.com"


@pytest.mark.headed
@pytest.mark.noxvfb
def test_manage_cookie_data(driver: Firefox):
    """
    C143633 - Cookies and Site Data can be managed
    via the "Managed Cookies and Site Data" pane.
    """
    # Initialize objects
    about_prefs = AboutPrefs(driver, category="privacy")
    ba = BrowserActions(driver)

    # Visit some sites to add cookies
    for site in [
        "https://www.google.com",
        "https://www.jetbrains.com",
        "https://www.wikipedia.com",
    ]:
        driver.get(site)
        sleep(1)

    # Open the Manage Cookies dialog
    about_prefs.open()
    about_prefs.open_manage_cookies_data_dialog()

    # Select and remove one cookie
    cookie_item = about_prefs.get_manage_data_site_element(COOKIE_SITE)
    cookie_item.click()
    assert cookie_item.get_attribute("selected") == "true"

    about_prefs.get_element("remove-selected-cookie-button").click()
    about_prefs.element_does_not_exist("manage-cookies-site", labels=[COOKIE_SITE])

    # Remove all cookies
    about_prefs.get_element("remove-all-button").click()
    sleep(1)
    cookie_list = about_prefs.get_elements("cookies-manage-data-sitelist")
    assert len(cookie_list) == 1

    # Save changes and handle confirmation alert
    about_prefs.get_element("manage-data-save-changes-button").click()
    sleep(1)

    try:
        alert = about_prefs.get_alert()
        logging.info(f"Alert text: {alert.text}")
        alert.accept()
        logging.info("Alert accepted successfully.")
    except Exception as e:
        logging.warning(f"No alert appeared or failed to handle: {e}")

    ba.switch_to_content_context()
    sleep(1)

    # Reopen and confirm cookies cleared
    about_prefs.open_manage_cookies_data_dialog()
    cookie_list_post_remove = about_prefs.get_elements("cookies-manage-data-sitelist")
    assert len(cookie_list_post_remove) == 1
    logging.info("All cookie data cleared successfully.")
