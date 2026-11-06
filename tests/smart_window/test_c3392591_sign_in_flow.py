"""
C3392591 - Verify that sign in flow is working
Choosing Smart in the Switch Windows panel while signed out opens FxA; signing
in there with an existing account's email and password signs Firefox in to
that account and shows the AI chat page.
"""

import pytest
from auto_fxui.browser_object import SmartWindow
from auto_fxui.classes.fxa_session import FxaSession
from auto_fxui.page_object import FxaHome


@pytest.fixture()
def test_case():
    return "3392591"


def test_sign_in_flow(driver, create_fxa: FxaSession, smart_window: SmartWindow):
    """
    C3392591 - Verify that sign in flow is working
    """
    # Instantiate objects
    fxa = FxaHome(driver)
    email = create_fxa.restmail.email

    # Start on a new tab, as a user would: it becomes the AI chat page once
    # the window turns Smart. about:blank, the default here, stays blank.
    driver.get("about:newtab")

    smart_window.open_window_switcher()
    smart_window.element_visible("switch-to-classic")
    smart_window.element_visible("switch-to-smart")
    smart_window.close_window_switcher()

    smart_window.open_smart_window_sign_in()
    fxa.element_visible("login-email-input")

    fxa.sign_up_sign_in(email)
    fxa.element_visible("login-password-input")

    # FxA closes its tab once Firefox has the account.
    fxa.fill_password(create_fxa.password)
    smart_window.expect_signed_in()
    assert smart_window.get_signed_in_email() == email
    smart_window.expect_smart_window_active(True)
    smart_window.expect_selected_tab_url_contains("aiwindow/aiWindow.html")
