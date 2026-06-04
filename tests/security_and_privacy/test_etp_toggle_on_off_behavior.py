import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TrustPanel
from modules.page_object import GenericPage

TEST_URL = "https://youtube.com/"


@pytest.fixture()
def test_case():
    return "3054034"


def test_etp_toggle_on_off_behavior(driver: Firefox, trust_panel: TrustPanel):
    """
    C3054034 - ETP toggle ON and OFF path are correctly working
    """

    # Instantiate objects
    test_page = GenericPage(driver, url=TEST_URL)

    # Open test page and click on the shield icon
    test_page.open()
    trust_panel.open_panel()

    # Click the blue switch to OFF
    trust_panel.trustpanel_toggle_on_off()

    # Site reloads; shield icon shows disabled state
    trust_panel.element_visible("shield-icon-disabled")
    trust_panel.open_panel()

    # Toggle turns gray
    trust_panel.element_visible("trustpanel-tracking-protection-disabled")

    # Panel strings update to “You turned off protections”
    trust_panel.trustpanel_status("off")

    # Click the gray switch to turn ON the panel
    trust_panel.trustpanel_toggle_on_off()

    # The panel reverts to default
    trust_panel.open_panel()

    # Tracker blocking is active
    trust_panel.trustpanel_status("on")

    # Icon and UI updates to reflect the blocking trackers; "Firefox is on guard" text is displayed inside the card
    trust_panel.element_visible("trustpanel-header-enabled")
