import os
import re
import csv
import time
import pytest

from modules.page_object import AboutLogins
from pynput.keyboard import Controller

@pytest.fixture()
def test_case():
    return "2241522"


@pytest.mark.headed
def test_password_csv_correctness(driver_and_saved_logins, home_folder, sys_platform):
    """
    C2241521: Check that password.csv displays the correct information
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
    if sys_platform == "Linux":
        passwords_csv = os.path.join(home_folder, "Desktop", "passwords.csv")
        downloads_folder = os.path.join(home_folder, "Desktop")
    else:
        passwords_csv = os.path.join(home_folder, "Downloads", "passwords.csv")
        downloads_folder = os.path.join(home_folder, "Documents")
    # about_logins.wait.until(lambda _: os.path.exists(passwords_csv))

    # Verify the results
    guid_pattern = re.compile(r"{[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12}}")
    time_pattern = re.compile(r"[0-9]{10}")
    with open(passwords_csv) as pw:
        reader = csv.DictReader(pw)
        actual_logins = {}
        for row in reader:
            actual_logins[row["username"] + "@" + row["url"][8:]] = row["password"]
            assert re.match(guid_pattern, row["guid"])
            assert re.match(time_pattern, row["timeCreated"])
            assert re.match(time_pattern, row["timeLastUsed"])
            assert re.match(time_pattern, row["timeCreated"])
        assert "httpRealm" in row.keys()
        assert "formActionOrigin" in row.keys()
    about_logins.check_logins_present(actual_logins, logins)

    # Delete the password.csv created
    for file in os.listdir(downloads_folder):
        delete_files_regex = re.compile(r"\bpasswords.csv\b")
        if delete_files_regex.match(file):
            os.remove(passwords_csv)
