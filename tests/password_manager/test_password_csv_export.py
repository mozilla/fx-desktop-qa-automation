import os
import time

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

    # Ensure the export target folder doesn't contain a passwords.csv file
    about_logins.remove_password_csv("Downloads")
    about_logins.remove_password_csv("Documents")

    # Click on buttons to export passwords
    about_logins.open()
    about_logins.click_on("menu-button")
    about_logins.click_on("export-passwords-button")
    about_logins.click_on("continue-export-button")

    # Export the password file
    time.sleep(2)
    keyboard.tap(Key.enter)
    time.sleep(3)

    # Since CI machines seem to be affected by other tests, the default export directory can
    # change randomly. This checks if the file exists in any of the directories we've seen
    # the default get set to.
    subdirectories = ["Downloads", "Documents"]
    for directory in subdirectories:
        home = os.path.expanduser("~")
        sub_dir = os.path.join(home, directory)
        csv_file = os.path.join(sub_dir, "passwords.csv")
        try:
            if os.path.exists(csv_file):
                break
        except ValueError as e:
            print(f"Caught error: {e}, continuing to next iteration")
            continue
        print(f"Successfully completed iteration with sudirectories = {subdirectories}")

    # Delete the password.csv file created in possible directories
    about_logins.remove_password_csv("Downloads")
    about_logins.remove_password_csv("Documents")
