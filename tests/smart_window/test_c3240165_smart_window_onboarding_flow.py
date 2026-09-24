"""
C3240165 - Verify that the user can go through the entire Onboarding Flow
Signed in with an existing account, the Smart Window first run can be
completed with a chosen model, and its choices take effect.
"""

import pytest

from modules.browser_object import SmartWindow
from modules.classes.fxa_session import FxaSession
from modules.page_object import FxaHome, SmartWindowFirstRun


@pytest.fixture()
def test_case():
    return "3240165"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.smartwindow.firstrun.hasCompleted", False),
        ("browser.smartwindow.firstrun.modelChoice", ""),
    ]


def test_smart_window_onboarding_flow(
    driver, create_fxa: FxaSession, smart_window: SmartWindow
):
    """
    C3240165 - Verify that the user can go through the entire Onboarding Flow
    """
    # Sign in as an existing account through the Smart Window flow.
    smart_window.open_smart_window_sign_in()
    fxa = FxaHome(driver)
    fxa.inject_session(create_fxa)
    fxa.continue_with_cached_account()
    smart_window.expect_signed_in()
    smart_window.expect_first_run_view(True)

    first_run = SmartWindowFirstRun(driver)
    # Any offered model: this case is about the flow, not a specific model.
    first_run.complete_onboarding()

    # Onboarding ends on the Smart Window new tab with the nav-bar back.
    smart_window.expect_first_run_view(False)
    smart_window.expect_selected_tab_url_contains("aiwindow/aiWindow.html")

    first_run.expect_model_choice_saved()
    assert first_run.get_pref("browser.smartwindow.firstrun.hasCompleted") is True
    # "Make Smart Window the default" is checked by default.
    assert first_run.get_pref("browser.smartwindow.isDefaultWindow") is True
