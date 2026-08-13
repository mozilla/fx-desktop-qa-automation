import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TrustPanel
from modules.page_object import AboutPrefs, GenericPage


@pytest.fixture()
def test_case():
    return "446325"


TRACKER_URL = "https://www.itisatrap.org/firefox/its-a-tracker.html"


def test_tracking_elements_not_blocked_with_etp_disabled(
    driver: Firefox, trust_panel: TrustPanel, check_tracker_test_field
):
    """
    C446325: Verify tracking elements are not blocked in normal browsing session after ETP is disabled
    """
    about_prefs = AboutPrefs(driver, category="privacy")

    # Make sure that the "Standard" option is selected from the ETP section in about:preferences#privacy
    about_prefs.open()
    about_prefs.select_etp_level("standard")

    # open the trackers page
    tracker_website = GenericPage(driver, url=TRACKER_URL)
    tracker_website.open()

    # click on the shield icon
    trust_panel.open_panel()

    # turn off the enhanced tracking protection toggle
    trust_panel.trustpanel_toggle_on_off()

    # verify that the toggle has been turned off
    trust_panel.open_panel()
    trust_panel.trustpanel_status("off")

    check_tracker_test_field("third-party", correct=False)
    check_tracker_test_field("first-party")
    check_tracker_test_field("dnt", correct=False)
