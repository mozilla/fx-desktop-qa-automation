import os
import sys
import time
from os import environ

import pytest
from pynput.keyboard import Controller, Key

from modules.page_object import AboutLogins


@pytest.fixture()
def test_case():
    return "2241521"


MAC_GHA = environ.get("GITHUB_ACTIONS") == "true" and sys.platform.startswith("darwin")


@pytest.mark.headed
def test_password_csv_export(
    driver_and_saved_logins, home_folder, sys_platform, opt_ci
):
    """
    C2241521: Check that password.csv can be downloaded from about:logins
    """
    # Initializing objects
    (driver, usernames, logins) = driver_and_saved_logins
    about_logins = AboutLogins(driver)
    keyboard = Controller()

    # Ensure the Downloads folder doesn't contain a passwords.csv file
    about_logins.remove_password_csv(home_folder)

    # Click on buttons to export passwords
    about_logins.open()
    about_logins.click_on("menu-button")
    about_logins.click_on("export-passwords-button")
    about_logins.click_on("continue-export-button")

    # Download the password file
    time.sleep(5)
    keyboard.tap(Key.enter)

    # Verify that the file exists
    if sys_platform == "Linux":
        downloads_folder = os.getcwd()
    else:
        downloads_folder = os.path.join(home_folder, "Downloads")
    passwords_csv = os.path.join(downloads_folder, "passwords.csv")
    about_logins.wait.until(lambda _: os.path.exists(passwords_csv))

    # Delete the password.csv created
    about_logins.remove_password_csv(home_folder)
