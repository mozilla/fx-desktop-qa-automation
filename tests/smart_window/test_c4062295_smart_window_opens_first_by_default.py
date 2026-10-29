"""
C4062295 - A Smart Window opens first even if the last window was Classic
"""

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import SmartWindow


@pytest.fixture()
def test_case():
    return "4062295"


@pytest.fixture()
def use_persistent_profile():
    """The default-window pref has to survive the quit."""
    yield True


@pytest.fixture()
def fxa_env():
    """No FxA here; the autouse bypass would outlive the driver we quit."""
    return None


@pytest.fixture()
def add_to_prefs_list():
    """Add to the suite prefs; replacing them would drop first-run setup."""
    # Smart Window set as the default window type, which is what this asserts.
    return [("browser.smartwindow.isDefaultWindow", True)]


def test_smart_window_opens_first_by_default(driver: Firefox, restart_browser):
    """
    C4062295 - A Smart Window opens first even if the last window was Classic
    """
    smart_window = SmartWindow(driver)
    smart_window.activate_smart_window()

    # Leave the profile with a Classic window as the last state, so a restart
    # that simply restored what was open would come back Classic.
    smart_window.switch_to_classic_window()

    restarted = restart_browser(driver)
    SmartWindow(restarted).expect_smart_window_active(True)
