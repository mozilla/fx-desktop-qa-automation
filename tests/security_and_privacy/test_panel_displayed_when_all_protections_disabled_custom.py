import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TrustPanel
from modules.page_object import AboutPrefs, GenericPage

TEST_WEBSITE = "https://www.google.com/"


@pytest.fixture()
def test_case():
    return "3054908"


def test_panel_displayed_when_all_protections_disabled_custom(driver: Firefox):
    """
    C3054908 - The panel is correctly displayed when all protections are disabled through custom
    """

    # Instantiate objects
    about_prefs = AboutPrefs(driver, category="privacy")
    test_page = GenericPage(driver, url=TEST_WEBSITE)
    trust_panel = TrustPanel(driver)

    # Go to about:preferences#privacy and select the "Custom" options from the ETP section and deselect everything
    about_prefs.open()
    about_prefs.select_trackers_to_block()

    # Open page and click on the shield icon
    test_page.open()
    trust_panel.open_panel()
    # trust_panel.wait_for_trackers()

    # The message "Enhanced Tracking Protection is on" is displayed inside the banner
    trust_panel.trustpanel_etp_label_displayed_in_subpanel()
