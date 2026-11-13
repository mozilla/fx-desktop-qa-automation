"""
C4062295 - Verify that a Smart window is first opened even if the Last window was a Classic Firefox Window
With Smart Window set as the default, Firefox starts in a Smart Window even
when the window open at quit was Classic.
"""

import pytest
from auto_fxui.browser_object import SmartWindow
from auto_fxui.restart import restart_firefox
from selenium.webdriver import Firefox


@pytest.fixture()
def test_case():
    return "4062295"


@pytest.fixture()
def fxa_env():
    """No FxA: the WAF bypass is installed in the Firefox that restart_firefox quits."""
    return None


@pytest.fixture()
def add_to_prefs_list():
    return [("browser.smartwindow.isDefaultWindow", True)]


def test_smart_window_opens_first_by_default(
    driver: Firefox, active_smart_window: SmartWindow
):
    """
    C4062295 - Verify that a Smart window is first opened even if the Last window was a Classic Firefox Window
    """
    smart_window = active_smart_window
    smart_window.switch_to_classic_window()

    restart_firefox(driver)
    smart_window.expect_smart_window_active(True)
