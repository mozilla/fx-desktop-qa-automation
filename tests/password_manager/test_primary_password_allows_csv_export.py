import os

import pytest
from selenium.webdriver import Firefox

from modules.page_object_about_pages import AboutLogins
from modules.page_object_prefs import AboutPrefs
from modules.util import BrowserActions

TEST_PAGE_URL = "https://mozilla.github.io/"
USERNAME = "username1"
PASSWORD = "password1"
PRIMARY_PASSWORD = "securePassword1"
ALERT_MESSAGE = "Primary Password successfully changed."


@pytest.fixture()
def test_case():
    return "2241527"


def test_primary_password_allows_csv_export(driver: Firefox, downloads_folder):
    """
    C2241527 - Verify that entering the Primary Password allows successful export of passwords to a CSV file
    """

    # Instantiate objects
    about_logins = AboutLogins(driver)
    about_prefs = AboutPrefs(driver, category="privacy")
    ba = BrowserActions(driver)

    # Ensure the export target folder doesn't contain a passwords.csv file
    about_logins.remove_password_csv(downloads_folder)

    # Have a Primary Password set
    about_prefs.open()
    about_prefs.open_primary_password_popup(ba)
    about_prefs.set_primary_password(PRIMARY_PASSWORD)
    about_prefs.accept_alert_and_verify_text(ALERT_MESSAGE)

    # Have at least one saved login
    about_logins.open()
    about_logins.add_login(TEST_PAGE_URL, USERNAME, PASSWORD)

    # Click on the password "Copy" button to trigger primary password
    about_logins.click_copy_password_button()

    # Enter the correct Primary Password
    about_logins.enter_primary_password(PRIMARY_PASSWORD)

    # Export the passwords CSV
    about_logins.export_passwords_csv(downloads_folder, "passwords.csv")

    # Verify the exported csv file is present in the target folder
    csv_file = about_logins.verify_csv_export(downloads_folder, "passwords.csv")
    assert os.path.exists(csv_file)

    # Delete the password.csv created
    about_logins.remove_password_csv(downloads_folder)
