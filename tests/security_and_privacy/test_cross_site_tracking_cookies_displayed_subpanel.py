import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TrustPanel
from modules.page_object import AboutPrefs, GenericPage

COOKIES_URL = "https://senglehardt.com/test/trackingprotection/test_pages/tracking_protection.html"
DETECTED_COOKIES = ("https://social-track-digest256.dummytracker.org",
                    "https://ads-track-digest256.dummytracker.org",
                    "https://analytics-track-digest256.dummytracker.org"
                    )


@pytest.fixture()
def test_case():
    return "3054909"


def test_cross_site_tracking_cookies_displayed_subpanel(driver: Firefox):
    """
    C3054909 - Cross-site tracking cookies are correctly displayed in the sub panel
    """

    # Instantiate objects
    about_prefs = AboutPrefs(driver, category="privacy")
    tracking_page = GenericPage(driver, url=COOKIES_URL)
    trust_panel = TrustPanel(driver)

    # In about:preferences#privacy select only the option "Cross-site tracking cookies" in the Cookies section
    about_prefs.open()
    about_prefs.select_trackers_to_block("cookies-checkbox")

    # Open page and click on the shield icon
    tracking_page.open()
    trust_panel.open_panel()
    trust_panel.wait_for_trackers()

    # Click on "See All" button
    trust_panel.click_see_all()

    # Click on Cross-site tracking cookies
    trust_panel.open_detected_category("tracking cookies")

    # "Third-Party Cookies Blocked" title is displayed in the subpanel
    trust_panel.blocked_trackers_title_displayed_in_subpanel("third-party cookies")

    # The blocked cross-site tracking cookies are displayed inside the subpanel
    assert trust_panel.has_detected_tracking_sites(*DETECTED_COOKIES)
