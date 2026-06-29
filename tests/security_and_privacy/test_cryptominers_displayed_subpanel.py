import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TrustPanel
from modules.page_object import AboutPrefs, GenericPage

CRYPTOMINERS_URL = (
    "https://senglehardt.com/test/trackingprotection/test_pages/cryptomining.html"
)
DETECTED_CRYPTOMINER = "https://base-cryptomining-track-digest256.dummytracker.org"


@pytest.fixture()
def test_case():
    return "446403"


def test_cryptominers_displayed_subpanel(driver: Firefox):
    """
    C3054910 - Cryptominers are correctly displayed in the sub panel
    """

    # Instantiate objects
    about_prefs = AboutPrefs(driver, category="privacy")
    tracking_page = GenericPage(driver, url=CRYPTOMINERS_URL)
    trust_panel = TrustPanel(driver)

    # In about:preferences#privacy select only the option "Cryptominers"
    about_prefs.open()
    about_prefs.select_trackers_to_block("cryptominers-checkbox")

    # Open page and click on the shield icon
    tracking_page.open()
    trust_panel.open_panel()
    trust_panel.wait_for_trackers()

    # Click on "See All" button
    trust_panel.click_see_all()

    # Click on Cryptominers
    trust_panel.open_detected_category("cryptominer")

    # "Cryptominers Blocked" title is displayed in the subpanel
    trust_panel.blocked_trackers_title_displayed_in_subpanel("cryptominers")

    # The cryptominers blocked are displayed inside the subpanel
    assert trust_panel.has_detected_tracking_sites(DETECTED_CRYPTOMINER)
