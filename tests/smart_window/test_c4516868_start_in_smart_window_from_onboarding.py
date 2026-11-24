"""
C4516868 - Verify that the user can select to have Smart Window as default browser during onboarding
With Start in Smart Window on when onboarding ends, Firefox starts in a Smart
Window after it is closed and started again.
"""

import pytest
from auto_fxui.browser_object import SmartWindow
from auto_fxui.page_object import SmartWindowFirstRun
from selenium.webdriver import Firefox


@pytest.fixture()
def test_case():
    return "4516868"


@pytest.fixture()
def fxa_env():
    """No FxA: the WAF bypass is installed in the Firefox that restart() quits."""
    return None


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.smartwindow.firstrun.hasCompleted", False),
        ("browser.smartwindow.firstrun.modelChoice", ""),
    ]


def test_start_in_smart_window_from_onboarding(
    driver: Firefox, active_smart_window: SmartWindow
):
    """
    C4516868 - Verify that the user can select to have Smart Window as default browser during onboarding
    """
    smart_window = active_smart_window
    first_run = SmartWindowFirstRun(driver)

    smart_window.open_first_run()
    assert first_run.is_single_page(), "Expected the single-page onboarding"
    # The toggle starts on, so turn it off first to enable it as the case does.
    first_run.set_default_window(False)
    first_run.set_default_window(True)
    first_run.save()

    smart_window.expect_first_run_view(False)
    assert first_run.get_pref("browser.smartwindow.isDefaultWindow") is True

    smart_window.restart()
    smart_window.expect_smart_window_active(True)
