import time
import os
import re
import pytest

from modules.page_object import AboutLogins
from pynput.keyboard import Controller

@pytest.fixture()
def test_case():
    return "2241521"

@pytest.fixture()
def delete_files_regex_string():
    return r"\bpasswords.csv\b"


def test_about_logins_search_website(driver_and_saved_logins, home_folder, sys_platform):
    """
    C2241521: Check that the search function filters passwords correctly using websites
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
    about_logins.handle_os_download_confirmation(keyboard, sys_platform)

    # Verify that the file exists
    if sys_platform == "Windows":
        passwords_csv = os.path.join(home_folder, "Documents", "passwords.csv")
        downloads_folder = os.path.join(home_folder, "Documents")
    elif sys_platform == "Darwin":  # MacOS
        passwords_csv = os.path.join(home_folder, "Downloads", "passwords.csv")
        downloads_folder = os.path.join(home_folder, "Downloads")
    elif sys_platform == "Linux":
        passwords_csv = os.path.join(home_folder, "passwords.csv")
        downloads_folder = home_folder
    time.sleep(1)
    assert os.path.exists(passwords_csv), f"The file was not downloaded to {passwords_csv}."

    # Delete the password.csv created
    for file in os.listdir(downloads_folder):
        delete_files_regex = re.compile(r"\bpasswords.csv\b")
        if delete_files_regex.match(file):
            os.remove(passwords_csv)
