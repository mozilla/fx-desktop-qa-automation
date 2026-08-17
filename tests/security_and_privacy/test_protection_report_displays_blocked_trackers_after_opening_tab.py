import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TabBar
from modules.page_object import AboutProtections, AboutPrefs

TEST_WEBSITE = "https://www.bbc.com/"


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

    # Use Strict ETP mode
    about_prefs.open()
    about_prefs.select_etp_level("strict")

    # Reach "about:protections"
    protection.open()

    # There is no blocked tracker displayed on the page: "Firefox/Nightly blocked 0 trackers over the past week"
    assert protection.get_weekly_tracker_count() == 0

    # Visit a website that has trackers
    driver.get(TEST_WEBSITE)

    # Reach "about:protections"
    protection.open()

    # Wait for trackers to be counted
    protection.wait.until(lambda _: protection.get_weekly_tracker_count() > 0)

    # Get the current tracker count
    first_count = protection.get_weekly_tracker_count()

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
    protection.open()

    # The number of trackers is increasing with each site visit
    protection.wait.until(lambda _: protection.get_weekly_tracker_count() > first_count)
