"""
C3371305 - Verify that the user can go through the Onboarding process without
an existing account
A new user signs up through the Smart Window flow, then completes first-run
onboarding with a chosen model, and its choices take effect.
"""

import pytest
from fxa.tests.utils import TestEmailAccount

from modules.browser_object import SmartWindow
from modules.page_object import FxaHome, SmartWindowFirstRun


@pytest.fixture()
def test_case():
    return "3371305"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.smartwindow.firstrun.hasCompleted", False),
        ("browser.smartwindow.firstrun.modelChoice", ""),
    ]


def test_smart_window_onboarding_new_account(
    driver,
    restmail_session: TestEmailAccount,
    get_otp_code,
    smart_window: SmartWindow,
):
    """
    C3371305 - Verify that the user can go through the Onboarding process
    without an existing account
    """
    # Sign up as a new user; a new email gets a passwordless one-time code.
    smart_window.open_smart_window_sign_in()
    fxa = FxaHome(driver)
    fxa.sign_up_sign_in(restmail_session.email)
    fxa.fill_passwordless_code(get_otp_code(restmail_session))
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
