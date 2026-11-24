import pytest
from auto_fxui.browser_object import Devtools, Navigation, PanelUi, TrustPanel
from auto_fxui.page_object import AboutPrefs
from selenium.webdriver import Firefox

TEST_URL = "https://www.czyy.me/"
ETB_BLOCKED_MESSAGE = (
    "The resource at “https://s.adroll.com/j/roundtrip.js” was blocked because "
    "Enhanced Tracking Protection is enabled."
)
ETB_TRACKER_SITE = "s.adroll.com"
REMOTE_SETTINGS_SERVER = "https://firefox.settings.services.mozilla.com/v2"


@pytest.fixture()
def test_case():
    return "2119673"


@pytest.fixture()
def add_to_prefs_list():
    return [
        # Turns on tracking protection in private windows
        ("privacy.trackingprotection.pbmode.enabled", True),
        ("privacy.trackingprotection.emailtracking.pbmode.enabled", True),
        # Add remote settings to get the right tracker lists
        ("services.settings.server", REMOTE_SETTINGS_SERVER),
    ]


def test_etb_tracker_are_blocked_in_firefox(
    driver: Firefox, panel_ui: PanelUi, trust_panel: TrustPanel
):
    """
    C2119673 - The correct ETB trackers are blocked in a private window
    """

    # Instantiate objects
    nav = Navigation(driver)
    devtools = Devtools(driver)

    # Set ETP to Standard from about:preferences#privacy in a private window
    panel_ui.open_and_switch_to_new_window("private")
    private_about_prefs = AboutPrefs(driver, category="privacy")
    private_about_prefs.open()
    private_about_prefs.select_etp_level("standard")

    # Navigate to the test site
    nav.search(TEST_URL)

    # The console reports the ETB tracker as blocked, often ~20s after load
    devtools.custom_wait(timeout=60).until(
        lambda _: devtools.console_contains(ETB_BLOCKED_MESSAGE)
    )

    # Open the shield icon, click "See all" and open Tracking Content
    trust_panel.open_panel()
    trust_panel.wait_for_trackers(require_count=True)
    trust_panel.click_see_all()
    trust_panel.open_detected_category("tracking-content")

    # The ETB tracker is listed in the Tracking Content subpanel
    assert trust_panel.has_detected_tracking_sites(ETB_TRACKER_SITE)
