import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TrustPanel
from modules.page_object import AboutPrefs, GenericPage

YOUTUBE_URL = "https://www.youtube.com/"


@pytest.fixture()
def test_case():
    return "3054907"


def test_etp_panel_displayed_when_protection_off(driver: Firefox):
    """
    C3054907 - The ETP panel is correctly displayed when protection if turned off
    """

    # Instantiate objects
    about_prefs = AboutPrefs(driver, category="privacy")
    test_page = GenericPage(driver, url=YOUTUBE_URL)
    trust_panel = TrustPanel(driver)

    # Make sure that the "Standard" option is selected from the ETP section in about:preferences#privacy
    about_prefs.open()
    about_prefs.click_on("standard-radio")

    # Click on the shield icon and turn off the Enhanced Tracking Protection
    test_page.open()
    trust_panel.open_panel()
    trust_panel.trustpanel_toggle_on_off()
    trust_panel.open_panel()

    # The message "You turned off protections" is displayed inside the banner
    trust_panel.trustpanel_status("off")
