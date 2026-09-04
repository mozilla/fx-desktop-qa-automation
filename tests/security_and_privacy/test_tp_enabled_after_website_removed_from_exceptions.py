import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TabBar
from modules.browser_object_trust_panel import TrustPanel
from modules.page_object_generics import GenericPage
from modules.page_object_prefs import AboutPrefs

TEST_WEBSITE = "https://edition.cnn.com/"


@pytest.fixture()
def test_case():
    return "446435"


def test_tp_enabled_after_website_removed_from_exceptions(
    driver: Firefox,
    trust_panel: TrustPanel,
    tabs: TabBar,
):
    """
    C446435 - TP gets enabled if a website is removed from Exceptions
    """

    # Instantiate objects
    test_page = GenericPage(driver, url=TEST_WEBSITE)
    about_prefs = AboutPrefs(driver, category="privacy")

    # Access test website
    test_page.open()

    # Click on the shield icon and turn off Tracking protection via toggle button
    trust_panel.open_panel()
    trust_panel.trustpanel_toggle_on_off()

    # Site reloads; the shield icon reflects the disabled state
    trust_panel.element_visible("shield-icon-disabled")

    # Visit "about:preferences#privacy" and click on the "Manage Exceptions..." button
    about_prefs.open()
    about_prefs.open_etp_settings()
    about_prefs.open_manage_exceptions_dialog()

    # Click on the "Remove all Website" button from the dialog and save changes
    about_prefs.remove_all_exceptions_and_save()

    # Access again https://edition.cnn.com/ in a new tab
    tabs.open_and_switch_to_new_tab()
    test_page.open()

    # The website is accessed and the shield icon has a "✓" in it (ETP re-enabled)
    trust_panel.open_panel()
    trust_panel.trustpanel_status("on")
    trust_panel.element_visible("trustpanel-header-enabled")
