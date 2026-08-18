import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, PanelUi, TrustPanel
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

FIRST_TRACKER_WEBSITE = (
    "https://senglehardt.com/test/trackingprotection/test_pages/"
    "tracking_protection.html"
)
SECOND_TRACKER_WEBSITE = "https://www.itisatrap.org/firefox/its-a-tracker.html"


def test_third_party_content_blocked_private_browsing_cross_site(
    driver: Firefox, panel_ui: PanelUi, nav: Navigation, trust_panel: TrustPanel
):
    """
    C446323.1: Ensure that third party content is blocked correctly
    """
    # Instantiate objects
    panel_ui.open()
    tracker_website = GenericPage(driver, url=FIRST_TRACKER_WEBSITE)

    # Open a private window
    panel_ui.open_and_switch_to_new_window("private")

    # Open the website, check for trackers
    tracker_website.open()
    trust_panel.open_panel()
    trust_panel.wait_for_trackers()

    trust_panel.sites_blocked(BLOCKED_TRACKER_URL)


def test_third_party_content_blocked_private_browsing_allowed_tracking(
    driver: Firefox, panel_ui: PanelUi, nav: Navigation, trust_panel: TrustPanel
):
    """
    C446323.2: Ensure that some third party content is allowed
    """
    # Instantiate objects
    panel_ui.open()
    tracker_website = GenericPage(driver, url=FIRST_TRACKER_WEBSITE)

    # Open a private window
    panel_ui.open_and_switch_to_new_window("private")

    # Open the website, ensure the blocking is taking place by refreshing website until indicated
    tracker_website.open()
    trust_panel.open_panel()
    trust_panel.wait_for_trackers()

    trust_panel.sites_detected(ALLOWED_TRACKING_URLS)


def test_third_party_content_private_browsing_tracking_statuses(
    driver: Firefox,
    nav: Navigation,
    panel_ui: PanelUi,
    trust_panel: TrustPanel,
    check_tracker_test_field,
):
    """
    C446323.3: Ensure that the statuses of some third party content are loaded properly
    """
    # Instantiate objects
    panel_ui.open()
    tracker_website = GenericPage(driver, url=SECOND_TRACKER_WEBSITE)

    # Open a private window
    panel_ui.open_and_switch_to_new_window("private")

    # Open the tracker website
    tracker_website.open()
    trust_panel.open_panel()

    check_tracker_test_field("third-party")
    check_tracker_test_field("first-party")
    check_tracker_test_field("dnt", correct=False)
