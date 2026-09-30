"""
C3309859 - Smart Window restored after restart
Verify a Smart Window comes back as a Smart Window when the session is
restored after a restart.
"""

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import SmartWindow


@pytest.fixture()
def test_case():
    return "3309859"


@pytest.fixture()
def use_persistent_profile():
    """Firefox must write session state into a profile that survives the quit."""
    yield True


@pytest.fixture()
def fxa_env():
    """
    Opt out of the FxA WAF bypass: this test never touches FxA.

    The suite sets fxa_env="stage", which makes the autouse fxa_waf_bypass
    fixture install a header against the *original* driver. restart_browser
    quits that driver, so the fixture's teardown then talks to a dead
    geckodriver and raises ConnectionRefused. Returning None makes the bypass
    a no-op (it early-returns when fxa_url is falsy).
    """
    return None


@pytest.fixture()
def add_to_prefs_list():
    """
    Add to the suite's prefs rather than replacing them: the suite baseline
    marks first run complete and picks a model, and overriding prefs_list
    outright would drop both and land this test in onboarding instead.
    """
    # 3 = restore the previous session on start, which is what carries the
    # Smart Window state across the restart.
    return [("browser.startup.page", 3)]


def test_smart_window_restored_after_restart(driver: Firefox, restart_browser):
    """
    C3309859 - Smart Window restored after restart
    """
    smart_window = SmartWindow(driver)
    smart_window.activate_smart_window()
    smart_window.expect_smart_window_active(True)

    # restart_browser quits first, so Firefox flushes session state on the way
    # out; killing it instead would leave nothing to restore.
    restarted = restart_browser(driver)

    SmartWindow(restarted).expect_smart_window_active(True)
