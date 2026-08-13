import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TrustPanel
from modules.page_object import AboutPrefs, GenericPage

YOUTUBE_URL = "https://www.youtube.com/"


@pytest.fixture()
def test_case():
    return "3054904"


def test_etp_panel_displayed_when_no_trackers_detected(
    driver: Firefox,
    trust_panel: TrustPanel,
):
    """
    C3054904 - The ETP panel is correctly displayed when no trackers are detected
    """

    # Instantiate objects
    about_prefs = AboutPrefs(driver, category="privacy")
    test_page = GenericPage(driver, url=YOUTUBE_URL)

    # Make sure that the "Standard" option is selected from the ETP section in about:preferences#privacy
    about_prefs.open()
    about_prefs.select_etp_level("standard")

    # Click on the shield icon
    test_page.open()
    trust_panel.open_panel()

    # The Tracking Protection Panel is correctly displayed
    trust_panel.trustpanel_status("on")
