import os
import pytest
from pynput.keyboard import Controller, Key

from modules.page_object import AboutLogins

PASSWORDS_FILE = "passwords.csv"


@pytest.fixture()
def test_case():
    return "2241521"


@pytest.mark.unstable(reason="Bug 1996005")
@pytest.mark.headed
@pytest.mark.noxvfb
def test_password_csv_export(
    driver_and_saved_logins, downloads_folder, sys_platform, opt_ci
):
    """
    C2241521: Verify that a password.csv file can be exported from about:logins
    """
    # Initializing objects
    (driver, usernames, logins) = driver_and_saved_logins
    about_logins = AboutLogins(driver)
    keyboard = Controller()

    # Ensure the export target folder doesn't contain a passwords.csv file
    about_logins.remove_password_csv(downloads_folder)

    # Export the passwords CSV
    about_logins.export_passwords_csv(downloads_folder, "passwords.csv")

    keyboard.tap(Key.enter)

    # Verify the exported csv file is present in the target folder
    csv_file = about_logins.verify_csv_export(downloads_folder, "passwords.csv")
    assert os.path.exists(csv_file)

    # Delete the password.csv created
    about_logins.remove_password_csv(downloads_folder)
