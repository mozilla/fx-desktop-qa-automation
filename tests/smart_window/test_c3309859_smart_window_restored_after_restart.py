"""
C3309859 - Smart Window restored after restart
Verify a Smart Window comes back as a Smart Window when the session is
restored after a restart.
"""

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import SmartWindow, TabBar

URL = "about:robots"


@pytest.fixture()
def test_case():
    return "3309859"


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
    # 3 = restore the previous session, which carries the Smart Window state.
    return [("browser.startup.page", 3)]


def test_smart_window_restored_after_restart(driver: Firefox, restart_browser):
    """
    C3309859 - Smart Window restored after restart
    """
    smart_window = SmartWindow(driver)
    driver.get(URL)
    smart_window.activate_smart_window()
    smart_window.expect_smart_window_active(True)

    # restart_browser quits first, so Firefox flushes session state on the way
    # out; killing it instead would leave nothing to restore.
    restarted = restart_browser(driver)

    SmartWindow(restarted).expect_smart_window_active(True)
    # The page comes back too, so this is the restored window rather than a
    # fresh one that happens to be Smart.
    TabBar(restarted).expect_title_contains("Gort")
    assert len(restarted.window_handles) == 1, "session restore duplicated the tab"
