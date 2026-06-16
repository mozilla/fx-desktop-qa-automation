import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TrustPanel
from modules.browser_object_tabbar import TabBar
from modules.page_object import GenericPage
from modules.page_object_prefs import AboutPrefs

TEST_URL = "https://senglehardt.com/test/trackingprotection/test_pages/fingerprinting_and_cryptomining_and_cookies.html"

TRACKING_URL = "https://senglehardt.com/test/trackingprotection/test_pages/tracking_protection.html/"

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
    test_page = GenericPage(driver, url=TEST_URL)
    tracking_page = GenericPage(driver, url=TRACKING_URL)

    # Use Standard ETP mode
    about_prefs_privacy.open()
    about_prefs_privacy.open_etp_advanced_settings()
    about_prefs_privacy.select_etp_level("standard")

    # Open test page and click on the shield icon
    test_page.open()
    trust_panel.open_panel()
    trust_panel.wait_for_trackers()

    # Click on the "See All" button
    trust_panel.click_see_all()

    # The trackers blocked on the page are listed under the section "Firefox blocked these things for you:"
    # which includes: "x Cross-site tracking cookies", "x Fingerprinters" and "x Cryptominer"
    trust_panel.detected_category_visible("cryptominer")
    trust_panel.detected_category_visible("fingerprinter")
    trust_panel.detected_category_visible("tracking cookies")

    # Tracking content is not blocked and is shown separately under the section "Firefox allowed these things so sites
    # don't break:", which includes: "Tracking content"
    trust_panel.detected_category_visible("tracking content")

    # Click on "Fingerprinter"
    trust_panel.open_detected_category("fingerprinter")

    # "Fingerprinters Blocked" title is displayed in the subpanel
    trust_panel.blocked_trackers_title_displayed_in_subpanel("fingerprinters")

    # The blocked fingerprinter is displayed inside the subpanel
    assert trust_panel.has_detected_tracking_sites(DETECTED_FINGERPRINTER)

    # Open tracking test page
    tabs.open_and_switch_to_new_tab()
    tracking_page.open()

    # Click on the shield icon -> "See All" button
    trust_panel.open_panel()
    trust_panel.wait_for_trackers()
    trust_panel.click_see_all()

    # The trackers blocked on the page are listed under the section "Firefox blocked these things for you:",
    # which includes: "x Cross-site tracking cookies"
    trust_panel.detected_category_visible("tracking cookies")
