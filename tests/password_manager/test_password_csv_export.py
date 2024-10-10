import os
import re
import time

import pytest
from pynput.keyboard import Controller, Key

from modules.page_object import AboutLogins


@pytest.fixture()
def test_case():
    return "2241521"


@pytest.mark.headed
def test_password_csv_export(
    driver_and_saved_logins, home_folder, sys_platform, opt_ci
):
    """
    C2241521: Check that password.csv can be downloaded from about:logins
    """
    # Initializing objects
    (driver, usernames, logins) = driver_and_saved_logins
    about_logins = AboutLogins(driver).open()
    keyboard = Controller()

    # Click on buttons to export passwords
    about_logins.click_on("menu-button")
    about_logins.click_on("export-passwords-button")
    about_logins.click_on("continue-export-button")

    # Download the password file
    time.sleep(4)
    keyboard.tap(Key.enter)

    # Verify that the file exists
    if sys_platform == "Linux":
        downloads_folder = os.getcwd()
    else:
        downloads_folder = os.path.join(home_folder, "Downloads")
    passwords_csv = os.path.join(downloads_folder, "passwords.csv")
    about_logins.wait.until(lambda _: os.path.exists(passwords_csv))

    # Delete the password.csv created
    for file in os.listdir(downloads_folder):
        delete_files_regex = re.compile(r"\bpasswords.csv\b")
        if delete_files_regex.match(file):
            os.remove(passwords_csv)
