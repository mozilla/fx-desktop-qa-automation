import csv
import logging
import time
import os
import re

import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutLogins
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from pynput.keyboard import Controller, Key
from modules.util import BrowserActions
from modules.browser_object import Navigation

@pytest.fixture()
def test_case():
    return "2241521"

@pytest.fixture()
def delete_files_regex_string():
    return r"\bpasswords.csv\b"


def test_about_logins_search_website(driver_and_saved_logins, home_folder, sys_platform, delete_files):
    """
    C2241521: Check that the search function filters passwords correctly using websites
    """
    # Initializing objects
    (driver, usernames, logins) = driver_and_saved_logins
    about_logins = AboutLogins(driver).open()
    keyboard = Controller()

    ba = BrowserActions(driver)
    nav = Navigation(driver)

    about_logins.click_on("menu-button")
    about_logins.click_on("export-passwords-button")
    about_logins.click_on("continue-export-button")

    time.sleep(4)
    about_logins.handle_os_download_confirmation(keyboard, sys_platform)

    # Set the expected download path and the expected file name
    passwords_csv = os.path.join(home_folder, "Downloads", "passwords.csv")

    # Verify if the file exists
    assert os.path.exists(
        passwords_csv
    ), f"The file was not downloaded to {saved_pdf_location}."

    guid_pattern = re.compile(r"{[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12}}")
    with open(passwords_csv) as pw:
        reader = csv.DictReader(pw)
        actual_logins = {}
        for row in reader:
            logging.info(row)
            origin = row["url"][8:]
            actual_logins[row["username"] + "@" + origin] = row["password"]
            assert re.match(guid_pattern, row["guid"])
    about_logins.check_logins_present(actual_logins, logins)
