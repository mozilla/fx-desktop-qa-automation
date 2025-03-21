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
    C2241521: Verify that a password.csv file can be exported from about:logins
    """
    # Initializing objects
    (driver, usernames, logins) = driver_and_saved_logins
    about_logins = AboutLogins(driver)
    keyboard = Controller()

    # Ensure the export target folder doesn't contain a passwords.csv file
    about_logins.remove_password_csv()

    # Click on buttons to export passwords
    about_logins.open()
    about_logins.click_on("menu-button")
    about_logins.click_on("export-passwords-button")
    about_logins.click_on("continue-export-button")

    # Download the password file
    time.sleep(5)
    keyboard.tap(Key.enter)

    # Verify the exported csv file is present in the target folder
    documents_directory = about_logins.get_documents_dir()
    csv_file = os.path.join(documents_directory, "passwords.csv")
    about_logins.wait.until(lambda _: os.path.exists(csv_file))

    # Delete the password.csv created
    about_logins.remove_password_csv()
