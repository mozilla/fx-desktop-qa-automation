import pytest
from selenium.webdriver import Firefox

from modules.browser_object_trust_panel import TrustPanel
from modules.page_object_generics import GenericPage
from modules.page_object_prefs import AboutPrefs

TRACKING_CONTENT_URL = "https://senglehardt.com/test/trackingprotection/test_pages/cryptomining_and_trackers"


@pytest.fixture()
def test_case():
    return "3054914"


def test_tracking_content_subpanel_display_when_not_blocked(driver: Firefox):
    """
    C3054914 - Cross-site tracking cookies are correctly displayed in the sub panel when they are not blocked
    """

    # Instantiate objects
    about_prefs = AboutPrefs(driver, category="privacy")
    tracking_page = GenericPage(driver, url=TRACKING_CONTENT_URL)
    trust_panel = TrustPanel(driver)

    # In about:preferences#privacy deselect only the option "Tracking content"
    # and from the Cookies section, select "Cookies from unvisited websites"
    about_prefs.open()
    about_prefs.select_trackers_to_block(
        "cookies-isolate-social-media-option",
        "known-fingerprints-checkbox",
        "suspected-fingerprints-checkbox",
        "cryptominers-checkbox",
        "cookies-from-unvisited-websites"
    )

    # Open page and click on the shield icon
    tracking_page.open()
    trust_panel.open_panel()
    trust_panel.wait_for_trackers()

    # Click on "See All" button
    trust_panel.click_see_all()

    # Click on "Cross-site tracking cookies"
    trust_panel.wait_for_trackers()
    trust_panel.js_click_on("cryptominers-detected")

    # "Not Blocking Cross-site Tracking Cookies." title is displayed in the subpanel
    trust_panel.title_displayed_in_subpanel("tracking content")

    # The allowed cross-site tracking cookies are displayed inside the subpanel
    assert trust_panel.has_allowed_sites()
