import csv
import os
import re
import time

import pytest

from modules.page_object import AboutLogins, GenericPage


@pytest.fixture()
def test_case():
    return "2241522"


@pytest.mark.headed
def test_password_csv_correctness(
    driver_and_saved_logins, downloads_folder, sys_platform
):
    """
    C2241522: Verify than an exported password.csv file displays the correct information
    """
    # Initializing objects
    (driver, usernames, logins) = driver_and_saved_logins
    about_logins = AboutLogins(driver)
    page = GenericPage(driver)

    # Ensure the export target folder doesn't contain a passwords.csv file
    about_logins.remove_password_csv(downloads_folder)

    # Click on buttons to export passwords
    about_logins.open()
    about_logins.click_on("menu-button")
    about_logins.click_on("export-passwords-button")
    about_logins.click_on("continue-export-button")

    # Export the password file
    time.sleep(3)
    page.navigate_dialog_to_location(downloads_folder)

    # Verify the exported csv file is present in the target folder
    csv_file = os.path.join(downloads_folder, "passwords.csv")
    about_logins.wait.until(lambda _: os.path.exists(csv_file))

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

    # Delete the password.csv created
    about_logins.remove_password_csv(downloads_folder)
