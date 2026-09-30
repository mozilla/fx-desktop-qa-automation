"""
C3392590 - Sign up through the Smart Window flow without a captcha
Signing up from the Switch Windows panel reaches FxA stage directly (no
"Client Challenge" captcha), completes as a passwordless sign-up, and opens
the Smart Window first run.
"""

import pytest
from fxa.tests.utils import TestEmailAccount

from modules.browser_object import SmartWindow
from modules.page_object import FxaHome

FXA_STAGE_HOST = "accounts.stage.mozaws.net"


@pytest.fixture()
def test_case():
    return "3392590"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.smartwindow.firstrun.hasCompleted", False),
        ("browser.smartwindow.firstrun.modelChoice", ""),
    ]


def test_smart_window_signup_skips_captcha(
    driver,
    restmail_session: TestEmailAccount,
    get_otp_code,
    smart_window: SmartWindow,
):
    """
    C3392590 - Sign up through the Smart Window flow without a captcha
    """
    smart_window.open_smart_window_sign_in()
    smart_window.expect_selected_tab_url_contains(FXA_STAGE_HOST)

    # With the fxa-ci header (fxa_waf_bypass fixture), stage serves FxA itself
    # rather than its "Client Challenge" captcha page.
    fxa = FxaHome(driver)
    fxa.element_visible("login-email-input")
    fxa.element_does_not_exist("captcha-container")

    # A new email goes straight to a passwordless one-time code.
    fxa.sign_up_sign_in(restmail_session.email)
    fxa.fill_passwordless_code(get_otp_code(restmail_session))

    # Firefox signs in and switches the window to Smart on its own.
    smart_window.expect_signed_in()
    smart_window.expect_smart_window_active(True)
    smart_window.expect_first_run_view(True)
    smart_window.expect_selected_tab_url_contains("aiwindow/firstrun.html")
