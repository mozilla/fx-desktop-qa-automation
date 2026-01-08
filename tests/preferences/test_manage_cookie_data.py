import logging
from time import sleep

import pytest
from selenium.webdriver import Firefox

from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "143633"


COOKIE_SITE = "google.com"
TEST_SITES = [
    "https://www.google.com",
    "https://www.jetbrains.com",
    "https://www.wikipedia.com",
]


@pytest.fixture()
def about_prefs_category():
    return "privacy"


@pytest.mark.noxvfb
def test_manage_cookie_data(driver: Firefox, about_prefs: AboutPrefs):
    """
    C143633 - Cookies and Site Data can be managed via the "Managed Cookies and Site Data" panel.
    """
    # Initialize objects

    # Visit some sites to add cookies
    for site in TEST_SITES:
        driver.get(site)

    # Open the Manage Cookies dialog
    about_prefs.open()
    about_prefs.open_manage_cookies_data_dialog()

    # Select and remove one cookie
    about_prefs.remote_cookie_site_data(COOKIE_SITE)

    # Remove all cookies
    about_prefs.remote_cookie_site_data(all_sites=True)

    # Save changes and handle confirmation alert
    about_prefs.click_on("manage-data-save-changes-button")

    try:
        alert = about_prefs.get_alert()
        logging.info(f"Alert text: {alert.text}")
        alert.accept()
        logging.info("Alert accepted successfully.")
    except Exception as e:
        logging.warning(f"No alert appeared or failed to handle: {e}")

    about_prefs.switch_to_default_frame()

    # Reopen and confirm cookies cleared
    about_prefs.open_manage_cookies_data_dialog()
    cookie_list_post_remove = about_prefs.get_elements("cookies-manage-data-sitelist")
    assert len(cookie_list_post_remove) == 1
