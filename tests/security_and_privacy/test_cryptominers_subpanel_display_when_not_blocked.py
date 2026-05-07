import pytest
from selenium.webdriver import Firefox

from modules.browser_object_trust_panel import TrustPanel
from modules.page_object_generics import GenericPage
from modules.page_object_prefs import AboutPrefs

CRYPTOMINERS_URL = (
    "https://senglehardt.com/test/trackingprotection/test_pages/cryptomining.html"
)

DETECTED_TRACKER_URL = "https://base-cryptomining-track-digest256.dummytracker.org"


@pytest.fixture()
def test_case():
    return "3054916"


def test_cryptominers_subpanel_display_when_not_blocked(driver: Firefox):
    """
    C3054915 - Cryptominers are correctly displayed in the sub panel when they are not blocked
    """

    # Instantiate objects
    about_prefs = AboutPrefs(driver, category="privacy")
    tracking_page = GenericPage(driver, url=CRYPTOMINERS_URL)
    trust_panel = TrustPanel(driver)

    # In about:preferences#privacy deselect only the option "Cryptominers" in the Cookies section
    about_prefs.open()
    about_prefs.select_trackers_to_block(
        "cookies-isolate-social-media-option",
        "tracking-checkbox",
        "known-fingerprints-checkbox",
        "suspected-fingerprints-checkbox"
    )

    # Open page and click on the shield icon
    tracking_page.open()
    trust_panel.open_panel()
    trust_panel.wait_for_trackers()

    # Click on "See All" button
    trust_panel.click_see_all()

    # Click on "Fingerprinters"
    trust_panel.wait_for_trackers()
    trust_panel.js_click_on("cryptominers-detected")

    # "Not Blocking Cryptominers" title is displayed in the subpanel
    trust_panel.title_displayed_in_subpanel("cryptominers")

    # The allowed cryptominers are displayed inside the subpanel
    assert trust_panel.has_allowed_sites()
