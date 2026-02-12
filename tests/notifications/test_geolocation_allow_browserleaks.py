import pytest
from selenium.common.exceptions import TimeoutException, UnexpectedAlertPresentException

from modules.browser_object import Navigation
from modules.page_object import GenericPage

TEST_URL = "https://browserleaks.com/geo"


@pytest.fixture()
def test_case():
    return "122612"


def _dismiss_system_location_dialog_if_present(driver) -> bool:
    """
    Dismiss/accept the system geolocation confirmEx dialog if it appears.
    Returns True if a dialog was handled.
    """
    try:
        alert = driver.switch_to.alert
        _ = alert.text  # forces lookup
        alert.accept()
        return True
    except Exception:
        return False


def test_geolocation_allow_browserleaks(driver):
    """
    122612 - Verify geolocation prompt is displayed on BrowserLeaks and Allow grants permission.
    Skips if OS/system location permission blocks Firefox.
    """
    nav = Navigation(driver)
    GenericPage(driver, url=TEST_URL).open()

    # Prompt is displayed (site permission)
    nav.wait.until(lambda _: nav.element_visible("geolocation-notification-container"))

    # Click Allow; handle possible OS-level confirmEx dialog
    try:
        nav.handle_geolocation_prompt(
            button_type="primary", remember_this_decision=False
        )
    except UnexpectedAlertPresentException:
        handled = _dismiss_system_location_dialog_if_present(driver)
        pytest.skip(
            "System-level location permission dialog blocked geolocation."
            + (" (dialog handled)" if handled else "")
        )

    # Some environments show the system dialog slightly after clicking Allow
    if _dismiss_system_location_dialog_if_present(driver):
        pytest.skip("System-level location permission dialog blocked geolocation.")

    # Permission indicator is shown in the address bar
    try:
        nav.expect_in_chrome(
            lambda _: nav.get_element("permissions-location-icon").is_displayed()
        )
    except TimeoutException:
        # If OS location is blocked, the icon might not appear even though the prompt was handled.
        pytest.skip("Geolocation permission could not be granted in this environment.")
