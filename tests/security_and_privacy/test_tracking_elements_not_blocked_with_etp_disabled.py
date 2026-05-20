import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TrustPanel
from modules.page_object import AboutPrefs, GenericPage


@pytest.fixture()
def test_case():
    return "446325"


TRACKER_URL = "https://www.itisatrap.org/firefox/its-a-tracker.html"


def test_tracking_elements_not_blocked_with_etp_disabled(
    driver: Firefox, trust_panel: TrustPanel
):
    """
    C446325: Verify tracking elements are not blocked in normal browsing session after ETP is disabled
    """
    about_prefs = AboutPrefs(driver, category="privacy")

    # Make sure that the "Standard" option is selected from the ETP section in about:preferences#privacy
    about_prefs.open()
    about_prefs.click_on("standard-radio")

    # open the trackers page
    tracker_website = GenericPage(driver, url=TRACKER_URL)
    tracker_website.open()

    # click on the shield icon
    trust_panel.open_panel()

    # turn off the enhanced tracking protection toggle
    trust_panel.trustpanel_toggle_on_off()
    trust_panel.wait_for_trackers()

    # Assert the various statuses, ensure that the correct one is displayed
    block_status = tracker_website.get_element(
        "simulated-third-party-tracker-load-status"
    )
    load_status = tracker_website.get_element(
        "simulated-first-party-tracker-load-status"
    )
    dnt_status = tracker_website.get_element("simulated-tracker-dnt-status")

    assert "incorrect" in block_status.get_attribute("class")
    assert "correct" in load_status.get_attribute("class")
    assert "incorrect" in dnt_status.get_attribute("class")
