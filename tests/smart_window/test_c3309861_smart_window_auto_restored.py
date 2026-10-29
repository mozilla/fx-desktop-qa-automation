"""
C3309861 - Smart Window is automatically restored with "Open previous windows
and tabs" selected
"""

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import SmartWindow, TabBar

URL = "https://www.mozilla.org/"


@pytest.fixture()
def test_case():
    return "3309861"


@pytest.fixture()
def use_persistent_profile():
    """Firefox must write session state into a profile that survives the quit."""
    yield True


@pytest.fixture()
def fxa_env():
    """No FxA here; the autouse bypass would outlive the driver we quit."""
    return None


@pytest.fixture()
def add_to_prefs_list():
    """Add to the suite prefs; replacing them would drop first-run setup."""
    # 3 = "Open previous windows and tabs", the setting under test.
    return [("browser.startup.page", 3)]


def test_smart_window_auto_restored(driver: Firefox, restart_browser):
    """
    C3309861 - Smart Window is automatically restored with "Open previous
    windows and tabs" selected
    """
    smart_window = SmartWindow(driver)
    driver.get(URL)
    smart_window.activate_smart_window()

    restarted = restart_browser(driver)

    # Automatic: nothing asks for the session back, unlike C3309859.
    SmartWindow(restarted).expect_smart_window_active(True)
    TabBar(restarted).expect_title_contains("Internet for people")
