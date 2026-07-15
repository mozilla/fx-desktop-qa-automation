import os

import pytest

from modules.page_object import AboutLogins

PASSWORDS_FILE = "passwords_export.csv"


@pytest.fixture()
def test_case():
    return "2241521"


@pytest.fixture()
def add_to_prefs_list():
    # Disable the OS re-authentication prompt shown on export so the flow can
    # run headlessly in CI.
    return [("signon.management.page.os-auth.locked.enabled", False)]


def test_password_csv_export(driver_and_saved_logins, downloads_folder, opt_ci):
    """
    C2241521: Verify that a password.csv file can be exported from about:logins
    """
    # Initializing objects
    (driver, usernames, logins) = driver_and_saved_logins
    about_logins = AboutLogins(driver)

    # Ensure the export target folder doesn't contain the exported CSV yet
    about_logins.remove_password_csv(downloads_folder, PASSWORDS_FILE)

    # Export the passwords CSV
    about_logins.export_passwords_csv(downloads_folder, PASSWORDS_FILE)

    # Verify the exported csv file is present in the target folder
    csv_file = about_logins.verify_csv_export(downloads_folder, PASSWORDS_FILE)
    assert os.path.exists(csv_file)

    # Delete the exported CSV
    about_logins.remove_password_csv(downloads_folder, PASSWORDS_FILE)
