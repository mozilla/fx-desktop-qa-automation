import pytest
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver import Firefox
from selenium.webdriver.support.ui import WebDriverWait

from modules.page_object_prefs import AboutPrefs

# The Firefox Updates control shows one button whose label depends on update
# state. We can't restart Firefox in an automated run, so we only confirm that
# one of the two expected states is present.
UPDATE_BUTTON_STATES = {
    "up_to_date_button": "Check for updates",
    "update_available_button": "Restart to Update Firefox",
}


@pytest.fixture()
def about_prefs_category():
    # Firefox Updates moved to Settings > About Firefox (about:preferences#about).
    return "about"


@pytest.fixture()
def test_case():
    return "143572"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [("app.update.disabledForTesting", False)]


def test_check_for_updates(driver: Firefox, about_prefs: AboutPrefs):
    """
    C143572 - The check for updates button is available and responsive.

    Under Settings > About Firefox, the Firefox Updates button reads either
    "Restart to Update Firefox" (update available) or "Check for updates"
    (otherwise). The state resolves asynchronously (it briefly shows
    "Checking for updates…"), so wait for one of the expected buttons to appear.
    """
    about_prefs.open()

    def _update_button_present(_):
        # The button lives in the update-state shadow DOM; only the button for
        # the current state is rendered, so look for whichever one is present.
        for locator, label in UPDATE_BUTTON_STATES.items():
            element = about_prefs.get_element(locator)
            if element and label in (element.get_attribute("label") or ""):
                return locator
        return False

    # The shadow content re-renders while the update state resolves, so ignore
    # transient stale-element errors during the poll.
    found_locator = WebDriverWait(
        driver, 30, ignored_exceptions=[StaleElementReferenceException]
    ).until(
        _update_button_present,
        message="No update-state button (check-for-updates or restart) was found",
    )

    # Confirm the surfaced button is displayed, clickable, and correctly labeled.
    about_prefs.verify_element_is_interactable(
        found_locator, UPDATE_BUTTON_STATES[found_locator]
    )
