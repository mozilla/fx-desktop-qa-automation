import csv
import os
import re
from time import sleep

import pytest
from pynput.keyboard import Controller, Key

from modules.page_object import AboutLogins


@pytest.fixture()
def test_case():
    return "2241522"


@pytest.mark.headed
def test_password_csv_correctness(driver_and_saved_logins, sys_platform):
    """
    C2241522: Verify than an exported password.csv file displays the correct information
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

    # Verify the contents of the exported csv file
    csv_file_location = about_logins.check_csv_file_presence()
    guid_pattern = re.compile(
        r"{[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12}}"
    )
    time_pattern = re.compile(r"[0-9]{10}")
    try:
        about_logins.wait.until(lambda _: os.path.exists(csv_file_location))
        with open(csv_file_location) as pw:
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
    finally:
        # Delete the password.csv file created in possible directories
        about_logins.remove_password_csv(["Downloads", "Documents"])
