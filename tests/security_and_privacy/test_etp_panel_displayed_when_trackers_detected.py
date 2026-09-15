import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TabBar, TrustPanel
from modules.page_object import AboutPrefs, GenericPage

FINGERPRINTERS_URL = "https://senglehardt.com/test/trackingprotection/test_pages/fingerprinting_and_cryptomining_and_cookies.html"

TRACKING_URL = "https://senglehardt.com/test/trackingprotection/test_pages/tracking_protection.html"

DETECTED_FINGERPRINTER = "https://base-fingerprinting-track-digest256.dummytracker.org"


@pytest.fixture()
def test_case():
    return "3054905"


def test_etp_panel_displayed_when_trackers_detected(
    driver: Firefox,
    trust_panel: TrustPanel,
    about_prefs_privacy: AboutPrefs,
    tabs: TabBar,
):
    """
    C3054905 - The ETP panel is correctly displayed when the blocked trackers are detected
    """

    # Instantiate objects
    test_page = GenericPage(driver, url=FINGERPRINTERS_URL)
    tracking_page = GenericPage(driver, url=TRACKING_URL)

    # Select the "Standard" ETP level
    about_prefs_privacy.open()
    about_prefs_privacy.select_etp_level("standard")

    # Open test page and the shield panel
    test_page.open()
    trust_panel.open_panel()
    trust_panel.wait_for_trackers(require_count=True)

    # Click "See All"
    trust_panel.click_see_all()

    # Cookies, fingerprinters and cryptominers are listed as blocked
    trust_panel.detected_category_visible("cryptominer")
    trust_panel.detected_category_visible("fingerprinter")
    trust_panel.detected_category_visible("tracking cookies")

    # Tracking content is listed separately as allowed
    trust_panel.detected_category_visible("tracking content")

    # Open the "Fingerprinter" category
    trust_panel.open_detected_category("fingerprinter")

    # "Fingerprinters Blocked" title is displayed in the subpanel
    trust_panel.blocked_trackers_title_displayed_in_subpanel("fingerprinters")

    # The blocked fingerprinter is listed in the subpanel
    assert trust_panel.has_detected_tracking_sites(DETECTED_FINGERPRINTER)

    # Open the tracking test page in a new tab
    tabs.open_and_switch_to_new_tab()
    tracking_page.open()

    # Open the shield panel -> "See All"
    trust_panel.open_panel()
    trust_panel.wait_for_trackers(require_count=True)
    trust_panel.click_see_all()

    # Only cookies are listed as blocked on this page
    trust_panel.detected_category_visible("tracking cookies")

    # Detections are per-page: no fingerprinters or cryptominers here
    trust_panel.detected_category_not_visible("fingerprinter")
    trust_panel.detected_category_not_visible("cryptominer")
