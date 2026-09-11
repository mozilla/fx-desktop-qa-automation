import pytest
from selenium.webdriver import Firefox

from modules.browser_object import PanelUi, ReportBrokenSite
from modules.page_object import GenericPage

TEST_URL = "https://example.com/"

REASON = "slow"
DESCRIPTION = "The page takes a very long time to load."


@pytest.fixture()
def test_case():
    return "446413"


@pytest.fixture()
def add_to_prefs_list():
    """A negative FOG port drops the report ping, so no site is actually reported."""
    return [
        ("datareporting.healthreport.uploadEnabled", True),
        ("ui.new-webcompat-reporter.enabled", True),
        ("telemetry.fog.test.localhost_port", -1),
    ]


def test_report_broken_site(
    driver: Firefox, panel_ui: PanelUi, report_broken_site: ReportBrokenSite
):
    """
    C446413 - Users can report site issues via "Report broken site" item
    """

    # Instantiate objects
    test_page = GenericPage(driver, url=TEST_URL)

    # Go to test website
    test_page.open()

    # Hamburger menu > "Help and Report" > "Report broken site"
    panel_ui.navigate_to_report_broken_site()

    # Choose a reason from the "What's broken" section
    report_broken_site.select_reason(REASON)

    # Write a description and send the report
    report_broken_site.fill_description(DESCRIPTION)
    report_broken_site.send_report()

    # The sub panel is replaced by the confirmation one
    report_broken_site.report_sent_confirmation_displayed()

    # Click on the "Okay" button
    report_broken_site.click_okay()

    # The confirmation panel is dismissed
    report_broken_site.panel_is_dismissed()
