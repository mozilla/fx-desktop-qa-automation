import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from modules.browser_object import TrustPanel
from modules.page_object import AboutPrefs, GenericPage


@pytest.fixture()
def test_case():
    return "446325"


TRACKER_URL = "https://www.itisatrap.org/firefox/its-a-tracker.html"


def test_tracking_elements(driver: Firefox, trust_panel: TrustPanel):
    """
    C446325: Verify tracking elements are not blocked in normal browsing session after ETP is disabled
    """
    about_prefs = AboutPrefs(driver, category="privacy")

    # Make sure that the "Standard" option is selected from the ETP section in about:preferences#privacy
    about_prefs.open()
    about_prefs.click_on("standard-radio")

    # open the trackers page and save the current state of the page before changes
    GenericPage(driver, url=TRACKER_URL).open()

    # click on the shield icon
    trust_panel.open_panel()
    trust_panel.wait_for_trackers()

    # turn off the enhanced tracking protection toggle
    trust_panel.trustpanel_toggle_on_off()

    # Wait for fresh DOM to have correct values (re-fetches each poll)
    wait = WebDriverWait(driver, 10)

    wait.until(
        EC.text_to_be_present_in_element(
            (By.ID, "blacklisted-loaded"), "incorrectly loaded"
        )
    )
    wait.until(
        EC.text_to_be_present_in_element(
            (By.ID, "whitelisted-loaded"), "correctly loaded"
        )
    )
    wait.until(
        EC.text_to_be_present_in_element((By.ID, "dnt-off"), "incorrectly missing")
    )
