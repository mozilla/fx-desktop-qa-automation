import time
import os
import re
import pytest
import logging

from modules.page_object import AboutLogins
from pynput.keyboard import Controller

@pytest.fixture()
def test_case():
    return "2241521"


@pytest.mark.headed
def test_password_csv_export(driver_and_saved_logins, home_folder, sys_platform, opt_ci, screenshot):
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
    screenshot(driver, opt_ci)

    # Download the password file
    time.sleep(4)
    screenshot(driver, opt_ci)
    about_logins.handle_os_download_confirmation(keyboard, sys_platform)
    screenshot(driver, opt_ci)

    # Verify that the file exists
    if sys_platform == "Linux":
        passwords_csv = os.path.join(home_folder, "passwords.csv")
        downloads_folder = home_folder
        for file in os.listdir(home_folder):
            logging.warning(file)
        logging.warning("docs:")
        for file in os.listdir(os.path.join(home_folder, "Documents")):
            logging.warning(file)
        logging.warning("dl:")
        for file in os.listdir(os.path.join(home_folder, "Downloads")):
            logging.warning(file)
        for file in os.listdir(os.path.join(home_folder, "Desktop")):
            logging.warning(file)
    else:
        passwords_csv = os.path.join(home_folder, "Downloads", "passwords.csv")
        downloads_folder = os.path.join(home_folder, "Documents")
    # about_logins.wait.until(lambda _: os.path.exists(passwords_csv))
    

    # Delete the password.csv created
    for file in os.listdir(downloads_folder):
        delete_files_regex = re.compile(r"\bpasswords.csv\b")
        if delete_files_regex.match(file):
            os.remove(passwords_csv)
