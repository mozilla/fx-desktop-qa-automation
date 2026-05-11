import pytest
from selenium.webdriver import Firefox

from modules.browser_object_trust_panel import TrustPanel
from modules.page_object_generics import GenericPage
from modules.page_object_prefs import AboutPrefs

TRACKING_CONTENT_URL = "https://senglehardt.com/test/trackingprotection/test_pages/cryptomining_and_trackers"

DETECTED_TRACKING_CONTENT = (
    "https://social-track-digest256.dummytracker.org",
    "https://ads-track-digest256.dummytracker.org",
    "https://analytics-track-digest256.dummytracker.org",
)


@pytest.fixture()
def test_case():
    return "3054917"


def test_tracking_content_subpanel_display_when_not_blocked(driver: Firefox):
    """
    C3054917 - Tracking content is correctly displayed in the sub panel when they are not blocked
    """

    # Instantiate objects
    about_prefs = AboutPrefs(driver, category="privacy")
    tracking_page = GenericPage(driver, url=TRACKING_CONTENT_URL)
    trust_panel = TrustPanel(driver)

    # In about:preferences#privacy deselect only the option "Tracking Content" in the Custom section
    about_prefs.open()
    about_prefs.select_trackers_to_block(
        "cookies-isolate-social-media-option",
        "known-fingerprints-checkbox",
        "suspected-fingerprints-checkbox",
        "cryptominers-checkbox"
    )

    # Open page and click on the shield icon
    tracking_page.open()
    trust_panel.open_panel()
    trust_panel.wait_for_trackers()

    # Click on "See All" button
    trust_panel.click_see_all()

    # Click on "Tracking content"
    trust_panel.wait_for_trackers()
    trust_panel.open_detected_category("tracking content")

    # "Not Blocking Tracking Content" title is displayed in the subpanel
    trust_panel.wait_for_trackers()
    trust_panel.title_displayed_in_subpanel("tracking content")

    # The allowed tracking content is displayed inside the subpanel
    assert trust_panel.has_allowed_sites(*DETECTED_TRACKING_CONTENT)
