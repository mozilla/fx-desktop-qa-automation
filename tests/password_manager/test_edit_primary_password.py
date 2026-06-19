import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutPrefs
from modules.util import BrowserActions

PRIMARY_PASSWORD = "securePassword1"
ALERT_MESSAGE = "Primary Password successfully changed."
NEW_PRIMARY_PASSWORD = "securePasswordNew"


@pytest.fixture()
def test_case():
    return "2245180"


@pytest.fixture()
def hard_quit():
    return True


def test_edit_primary_password(driver: Firefox):
    """
    C2245180 - Verify that the Primary Password can be successfully changed
    """

    # Instantiate objects
    about_prefs = AboutPrefs(driver, category="passwordsAutofill")
    ba = BrowserActions(driver)

    # Have a Primary Password set
    about_prefs.create_primary_password(PRIMARY_PASSWORD, ALERT_MESSAGE, ba)

    # Change the Primary Password
    about_prefs.change_primary_password(
        PRIMARY_PASSWORD, NEW_PRIMARY_PASSWORD, ALERT_MESSAGE, ba
    )
