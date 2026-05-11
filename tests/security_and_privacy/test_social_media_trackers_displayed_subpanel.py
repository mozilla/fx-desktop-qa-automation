import pytest
from selenium.webdriver import Firefox

from modules.browser_object_trust_panel import TrustPanel
from modules.page_object_generics import GenericPage
from modules.page_object_prefs import AboutPrefs

SOCIAL_TRACKER_URL = "https://senglehardt.com/test/trackingprotection/test_pages/social_tracking_protection.html"

DETECTED_SOCIAL_MEDIA_TRACKERS = (
    "https://social-tracking-protection-facebook-digest256.dummytracker.org",
    "https://social-tracking-protection-linkedin-digest256.dummytracker.org",
    "https://social-tracking-protection-twitter-digest256.dummytracker.org",
)


@pytest.fixture()
def test_case():
    return "3054913"


def test_social_media_trackers_displayed_subpanel(driver: Firefox):
    """
    C3054913 - Social media trackers are correctly displayed in the sub panel
    """

    # Instantiate objects
    about_prefs = AboutPrefs(driver, category="privacy")
    tracking_page = GenericPage(driver, url=SOCIAL_TRACKER_URL)
    trust_panel = TrustPanel(driver)

    # "Custom" option is selected from the ETP section in about:preferences#privacy and everything is deselected
    about_prefs.open()

    # In about:preferences#privacy select only the option "Tracking content" - > In all Windows
    about_prefs.select_trackers_to_block(
        "tracking-checkbox", "tracking-in-all-windows"
    )

    # Open page and click on the shield icon
    tracking_page.open()
    trust_panel.open_panel()
    trust_panel.wait_for_trackers()

    # Click on "See All" button
    trust_panel.click_see_all()

    # Click on Social Media Trackers
    trust_panel.open_detected_category("3 social media trackers")

    # "Social Media Trackers Blocked" title is displayed in the subpanel
    trust_panel.wait_for_trackers()
    trust_panel.title_displayed_in_subpanel("social media trackers")

    # The blocked social-media trackers are displayed inside the subpanel
    assert trust_panel.has_allowed_sites(*DETECTED_SOCIAL_MEDIA_TRACKERS)
