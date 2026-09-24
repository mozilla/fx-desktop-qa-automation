from os import environ

import pytest
from modules.browser_object import SmartWindow
from modules.taskcluster import get_tc_secret


@pytest.fixture()
def suite_id():
    return ("S70279", "Smart Window")


@pytest.fixture()
def prefs_list(add_to_prefs_list: dict):
    """
    Smart Window ships disabled by default; every test in this suite needs the
    feature available before the window opens.

    First-run onboarding is marked complete with a model chosen, so a Smart
    Window opens straight to its normal view. Tests of sign-up or onboarding
    override add_to_prefs_list to reset these two prefs.

    With first run complete, Firefox opens the AI sidebar whenever a window
    becomes Smart; openByDefault is turned off so a newly activated Smart
    Window starts with the sidebar closed.
    """
    prefs = [
        ("browser.smartwindow.enabled", True),
        ("browser.smartwindow.firstrun.hasCompleted", True),
        # Choice id "1" (Gemini today). Set before launch, so it can't be
        # picked by name like SmartWindowFirstRun.select_model does.
        ("browser.smartwindow.firstrun.modelChoice", "1"),
        ("browser.smartwindow.sidebar.openByDefault", False),
    ]
    prefs.extend(add_to_prefs_list)
    return prefs


@pytest.fixture()
def add_to_prefs_list():
    return []


@pytest.fixture()
def smart_window(driver):
    """Provide the Smart Window BOM for a window still in the Classic state."""
    return SmartWindow(driver)


@pytest.fixture()
def fxa_env():
    if environ.get("TASKCLUSTER_ROOT_URL") and environ.get("FX_EXECUTABLE"):
        fxa_keys = get_tc_secret("ci_waf_token", level=1)
        environ["CI_WAF_TOKEN"] = fxa_keys.get("stage")
    return "stage"


@pytest.fixture()
def active_smart_window(driver):
    """
    Provide the Smart Window BOM with the window already in the Smart Window
    state, for tests about behaviour *inside* a Smart Window.

    See SmartWindow.activate_smart_window for why this does not go through the
    product's own (FxA-gated) entry points.
    """
    sw = SmartWindow(driver)
    sw.activate_smart_window()
    return sw
