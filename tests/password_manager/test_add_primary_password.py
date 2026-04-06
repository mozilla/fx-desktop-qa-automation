import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutPrefs
from modules.util import BrowserActions

PRIMARY_PASSWORD = "securePassword1"
ALERT_MESSAGE = "Primary Password successfully changed."


@pytest.fixture()
def test_case():
    return "2245178"


@pytest.fixture()
def hard_quit():
    return True


def test_add_primary_password(driver: Firefox):
    """
    C2245178: Verify that a primary password can be added in about:preferences#privacy
    """
    # Instantiate objects
    about_prefs = AboutPrefs(driver, category="privacy")
    ba = BrowserActions(driver)

    # Select the "Use a primary password" check box to trigger the "Change Primary Password" window
    about_prefs.open()
    about_prefs.open_primary_password_popup(ba)

    # Current password field is empty and cannot be changed
    about_prefs.element_attribute_contains("current-password", "disabled", "true")

    # Primary password can be changed
    about_prefs.set_primary_password(PRIMARY_PASSWORD)

    # Check that the pop-up appears
    about_prefs.accept_alert_and_verify_text(ALERT_MESSAGE)
