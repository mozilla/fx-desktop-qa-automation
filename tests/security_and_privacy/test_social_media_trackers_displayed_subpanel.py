import pytest
from selenium.webdriver import Firefox

from modules.browser_object_trust_panel import TrustPanel
from modules.page_object_generics import GenericPage
from modules.page_object_prefs import AboutPrefs

SOCIAL_TRACKER_URL = "https://senglehardt.com/test/trackingprotection/test_pages/social_tracking_protection.html"

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

    # Custom" option is selected from the ETP section in about:preferences#privacy and everything is deselected
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

    # "Social Media Trackers Blocked" title is displayed in the subpanel

    # The blocked social-media trackers are displayed inside the subpanel
