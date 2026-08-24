import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TabBar, TrustPanel
from modules.page_object import AboutPrefs, AboutProtections

TEST_WEBSITE = "https://senglehardt.com/test/trackingprotection/test_pages/tracking_protection.html"


@pytest.fixture()
def test_case():
    return "448309"


def test_protection_report_displays_blocked_trackers_after_opening_tab(driver: Firefox):
    """
    C448309 - Trackers are being displayed as blocked in Protection report only after opening the tab
    """

    # Instantiate objects
    protection = AboutProtections(driver)
    tabs = TabBar(driver)
    about_prefs = AboutPrefs(driver, category="privacy")
    trust_panel = TrustPanel(driver)

    # Use Strict ETP mode
    about_prefs.open()
    about_prefs.select_etp_level("strict")

    # Reach "about:protections"
    protection.open()

    # There is no blocked tracker displayed on the page: "Firefox/Nightly blocked 0 trackers over the past week"
    assert protection.get_weekly_tracker_count() == 0

    # Visit a website that has trackers
    driver.get(TEST_WEBSITE)

    # Confirm the trackers were blocked on this page before navigating away
    trust_panel.open_panel()
    trust_panel.wait_for_trackers(require_count=True)

    # Reach "about:protections" and wait for the trackers to be counted
    first_count = protection.wait_for_weekly_tracker_count(1)

    # Open "about:protections" in a new tab
    tabs.open_and_switch_to_new_tab()
    protection.open()

    # Trackers are displayed as blocked on the page
    assert protection.get_weekly_tracker_count() > 0

    # Refresh the "about:protections" page
    protection.open()

    # The same amount of trackers are displayed as blocked on the page
    same_count = protection.get_weekly_tracker_count()
    assert same_count == first_count, (
        f"Expected count {first_count} but got {same_count}"
    )

    # Open again https://www.bbc.com/ and refresh the website for a couple of times
    driver.get(TEST_WEBSITE)
    driver.refresh()
    driver.refresh()

    # Open "about:protections" in a new tab
    tabs.open_and_switch_to_new_tab()

    # The number of trackers is increasing with each site visit
    protection.wait_for_weekly_tracker_count(first_count + 1)
