import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.browser_object_tabbar import TabBar
from modules.browser_object_tracker_panel import TrackerPanel
from modules.page_object_generics import GenericPage
from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "446404"


FINGERPRINTERS_URL = (
    "https://senglehardt.com/test/trackingprotection/test_pages/fingerprinting.html"
)


def test_blocking_fingerprinter(
    driver: Firefox,
    nav: Navigation,
    about_prefs_privacy: AboutPrefs,
    tracker_panel: TrackerPanel,
    tabs: TabBar,
):
    """
    C446404: Blocking Fingerprinters
    """
    # Instantiate objects
    about_prefs_privacy.open()
    tracking_page = GenericPage(driver, url=FINGERPRINTERS_URL)

    # Select custom option and keep just known fingerprinters checked
    about_prefs_privacy.select_trackers_to_block("known-fingerprints-checkbox")

    # Switch to and new tab and access url snd verify the shield icon
    tabs.new_tab_by_button()
    tabs.wait_for_num_tabs(2)
    tabs.switch_to_new_tab()

    tracking_page.open()
    tracker_panel.wait_for_blocked_tracking_icon(nav, tracking_page)

    # Open the tracker panel and verify fingerprinters are visible
    nav.assert_blocked_trackers("known-fingerprints")
