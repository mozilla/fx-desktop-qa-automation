import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutPrefs


@pytest.fixture()
def about_prefs_category():
    # The Firefox Updates card lives in Settings > About Firefox.
    return "about"


@pytest.fixture()
def test_case():
    return "3374337"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [
        ("browser.settings-redesign.enabled", True),
        ("app.update.disabledForTesting", False),
    ]


def test_check_for_updates_button_works(driver: Firefox, about_prefs: AboutPrefs):
    """
    C3374337 - The "Check for updates" button in the "Firefox Updates" card works correctly.
    """
    about_prefs.open()

    # The page checks once on open, so wait for it to finish.
    about_prefs.element_visible("update-up-to-date-message")

    about_prefs.click_on("up_to_date_button")

    # The checking message shows and the button is grayed out.
    about_prefs.element_visible("update-checking-message")
    about_prefs.element_attribute_contains(
        "update-checking-message", "label", "Checking for updates"
    )
    about_prefs.element_attribute_is("update-checking-button", "disabled", "true")

    # No update is installed, the build is still up to date.
    about_prefs.element_visible("update-up-to-date-message")
