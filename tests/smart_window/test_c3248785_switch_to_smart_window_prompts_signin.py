"""
C3248785 - Switch to Smart Window from the Switch Windows button
Signed out, choosing Smart in the Switch Windows panel must send the user to
the FxA sign-in flow rather than switching the window.
"""

import pytest

from modules.browser_object_smart_window import SmartWindow

FXA_SIGN_IN_HOST = "accounts.firefox.com"


@pytest.fixture()
def test_case():
    return "3248785"


def test_switch_to_smart_window_prompts_signin(smart_window: SmartWindow):
    """
    C3248785 - Switch to Smart Window from the Switch Windows button
    """
    smart_window.open_window_switcher()
    smart_window.expect_switcher_selection("classic")
    smart_window.close_window_switcher()

    smart_window.click_switch_to_smart_window()

    # Sign-in is required first: the FxA flow opens in a new tab, tagged with
    # the Smart Window entrypoint.
    smart_window.expect_selected_tab_url_contains(FXA_SIGN_IN_HOST)
    signin_url = smart_window.get_selected_tab_url()
    assert "entrypoint=smartwindow" in signin_url, signin_url
    assert "service=smartwindow" in signin_url, signin_url

    # The window itself stays Classic until sign-in completes.
    assert not smart_window.is_smart_window_active()
