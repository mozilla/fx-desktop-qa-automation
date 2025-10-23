import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, PanelUi, TrackerPanel
from modules.page_object import GenericPage


@pytest.fixture()
def test_case():
    return "446323"


@pytest.fixture()
def add_to_prefs_list():
    return [("privacy.trackingprotection.pbmode.enabled", True)]


ALLOWED_TRACKING_URLS = {
    "https://content-track-digest256.dummytracker.org",
    "https://ads-track-digest256.dummytracker.org",
    "https://social-track-digest256.dummytracker.org",
    "https://analytics-track-digest256.dummytracker.org",
}
BLOCKED_TRACKER_URL = "https://content-track-digest256.dummytracker.org"

FIRST_TRACKER_WEBSITE = "https://senglehardt.com/test/trackingprotection/test_pages/tracking_protection.html"
SECOND_TRACKER_WEBSITE = "https://www.itisatrap.org/firefox/its-a-tracker.html"


def test_third_party_content_blocked_private_browsing_cross_site(driver: Firefox):
    """
    C446323.1: Ensure that third party content is blocked correctly
    """
    # Instantiate objects
    panel_ui = PanelUi(driver)
    panel_ui.open()
    nav = Navigation(driver)
    tracker_panel = TrackerPanel(driver)
    tracker_website = GenericPage(driver, url=FIRST_TRACKER_WEBSITE)

    # Open a private window
    panel_ui.open_and_switch_to_new_window("private")

    # Open the website, ensure the blocking is taking place by continuously refreshing website until indicated
    tracker_website.open()
    tracker_panel.wait_for_blocked_tracking_icon(nav, tracker_website)

    # Verify the indicator
    driver.set_context(driver.CONTEXT_CHROME)
    tracker_panel.verify_tracker_shield_indicator(nav)
    nav.open_tracker_panel()

    # verify the panel title
    tracker_panel_title = tracker_panel.get_element("tracker-title")
    assert (
        tracker_panel_title.get_attribute("innerHTML")
        == "Protections for senglehardt.com"
    )

    # Fetch the items in the cross site trackers
    cross_site_trackers = tracker_panel.open_and_return_cross_site_trackers()

    # Ensure that the correct blocked site is listed
    found_tracker = False
    for item in cross_site_trackers:
        if item.get_attribute("value") == BLOCKED_TRACKER_URL:
            found_tracker = True
    assert found_tracker


def test_third_party_content_blocked_private_browsing_allowed_tracking(driver: Firefox):
    """
    C446323.2: Ensure that some third party content is allowed
    """
    # Instantiate objects
    panel_ui = PanelUi(driver)
    panel_ui.open()
    nav = Navigation(driver)
    tracker_panel = TrackerPanel(driver)
    tracker_website = GenericPage(driver, url=FIRST_TRACKER_WEBSITE)

    # Open a private window
    panel_ui.open_and_switch_to_new_window("private")

    # Open the website, ensure the blocking is taking place by continuously refreshing website until indicated
    tracker_website.open()
    tracker_panel.wait_for_blocked_tracking_icon(nav, tracker_website)

    # Verify the indicator
    driver.set_context(driver.CONTEXT_CHROME)
    tracker_panel.verify_tracker_shield_indicator(nav)

    # Open the panel and verify the title
    nav.open_tracker_panel()
    tracker_panel_title = tracker_panel.get_element("tracker-title")
    assert (
        tracker_panel_title.get_attribute("innerHTML")
        == "Protections for senglehardt.com"
    )

    # Fetch allowed trackers
    allowed_trackers = tracker_panel.open_and_return_allowed_trackers()

    # Verify the correct ones are allowed
    for item in allowed_trackers:
        assert item.get_attribute("value") in ALLOWED_TRACKING_URLS


def test_third_party_content_private_browsing_tracking_statuses(driver: Firefox):
    """
    C446323.3: Ensure that the statuses of some third party content are loaded properly
    """
    # Instantiate objects
    panel_ui = PanelUi(driver)
    panel_ui.open()
    nav = Navigation(driver)
    tracker_panel = TrackerPanel(driver)
    tracker_website = GenericPage(driver, url=SECOND_TRACKER_WEBSITE)

    # Open a private window
    panel_ui.open_and_switch_to_new_window("private")

    # Open the tracker website
    tracker_website.open()
    tracker_panel.wait_for_blocked_tracking_icon(nav, tracker_website)

    # Verify the indicator
    tracker_panel.verify_tracker_shield_indicator(nav)

    # Assert the various statuses, ensure that the correct one is displayed
    block_status = tracker_website.get_element("simulated-tracker-block-status")
    load_status = tracker_website.get_element("simulated-tracker-load-status")
    dnt_status = tracker_website.get_element("simulated-tracker-dnt-status")

    assert "hidden" not in block_status.get_attribute("class")
    assert "hidden" not in load_status.get_attribute("class")
    assert "incorrect" in dnt_status.get_attribute("class")
