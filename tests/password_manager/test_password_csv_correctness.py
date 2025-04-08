import csv
import os
import re
import time

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

    # Verify the contents of the exported csv file
    guid_pattern = re.compile(
        r"{[0-9a-z]{8}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{4}-[0-9a-z]{12}}"
    )
    time_pattern = re.compile(r"[0-9]{10}")
    with open(csv_file) as pw:
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

    # Delete the password.csv file created in possible directories
    about_logins.remove_password_csv("Downloads")
    about_logins.remove_password_csv("Documents")
