import os

import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutLogins, AboutPrefs
from modules.util import BrowserActions

TEST_PAGE_URL = "https://mozilla.github.io/"
USERNAME = "username1"
PASSWORD = "password1"
PRIMARY_PASSWORD = "securePassword1"
ALERT_MESSAGE = "Primary Password successfully changed."


@pytest.fixture()
def test_case():
    return "2241527"


@pytest.fixture()
def add_to_prefs_list():
    # Disable OS re-auth on export; the primary-password prompt itself is
    # handled separately in the export flow.
    return [("signon.management.page.os-auth.locked.enabled", False)]


@pytest.mark.headed
@pytest.mark.noxvfb
def test_primary_password_allows_csv_export(driver: Firefox, downloads_folder):
    """
    C2241527 - Verify that entering the Primary Password allows successful export of passwords to a CSV file
    """

    # Instantiate objects
    about_logins = AboutLogins(driver)
    # Passwords moved out of Privacy & Security into their own Settings category.
    about_prefs = AboutPrefs(driver, category="passwordsAutofill")
    ba = BrowserActions(driver)

    # Ensure the export target folder doesn't contain a passwords.csv file
    about_logins.remove_password_csv(downloads_folder)

    # Have a Primary Password set
    about_prefs.create_primary_password(PRIMARY_PASSWORD, ALERT_MESSAGE, ba)

    # Have at least one saved login
    about_logins.open()
    about_logins.add_login(TEST_PAGE_URL, USERNAME, PASSWORD)

    # Click on the password "Copy" button to trigger primary password
    about_logins.click_copy_password_button()

    # Enter the correct Primary Password
    about_logins.enter_primary_password(PRIMARY_PASSWORD)

    # Export the passwords CSV (re-enter the primary password at the prompt)
    about_logins.export_passwords_csv(
        downloads_folder, "passwords.csv", primary_password=PRIMARY_PASSWORD
    )

    # Verify the exported csv file is present in the target folder
    csv_file = about_logins.verify_csv_export(downloads_folder, "passwords.csv")
    assert os.path.exists(csv_file)

    # Delete the passwords.csv created
    about_logins.remove_password_csv(downloads_folder)
