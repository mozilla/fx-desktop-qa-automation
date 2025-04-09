import os
from time import sleep

import pytest
from pynput.keyboard import Controller, Key

from modules.page_object import AboutLogins


@pytest.fixture()
def test_case():
    return "2241521"


@pytest.mark.headed
def test_password_csv_export(driver_and_saved_logins, sys_platform, opt_ci):
    """
    C2241521: Verify that a password.csv file can be exported from about:logins
    """
    # Initializing objects
    (driver, usernames, logins) = driver_and_saved_logins
    about_logins = AboutLogins(driver)
    keyboard = Controller()

    # Ensure the possible export target folders don't contain a passwords.csv file.
    # Doing so ensures we won't get the system dialog for choosing to overwrite existing file or not.
    about_logins.remove_password_csv(["Downloads", "Documents"])

    # Click on buttons to export passwords
    about_logins.open()
    about_logins.click_on("menu-button")
    about_logins.click_on("export-passwords-button")
    about_logins.click_on("continue-export-button")

    # Export the password file
    sleep(3)
    keyboard.tap(Key.enter)
    sleep(3)

    try:
        csv_file_location = about_logins.check_csv_file_presence()
        if os.path.exists(csv_file_location):
            print("passwords.csv file found")
        else:
            pytest.fail("passwords.csv file was not found!")
    finally:
        # Delete the password.csv file created in possible directories
        about_logins.remove_password_csv(["Downloads", "Documents"])
