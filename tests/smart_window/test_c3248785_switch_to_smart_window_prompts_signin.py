"""
C3248785 - Switch to Smart Window from the Switch Windows button
Signed out, choosing Smart in the Switch Windows panel must send the user to
the FxA sign-in flow rather than switching the window.
"""

from urllib.parse import urlparse

import pytest

from modules.browser_object import SmartWindow

# Firefox's own FxA host, used when the suite sets no FxA environment.
DEFAULT_FXA_HOST = "accounts.firefox.com"


@pytest.fixture()
def test_case():
    return "3248785"


def test_switch_to_smart_window_prompts_signin(
    smart_window: SmartWindow, fxa_url: str | None
):
    """
    C3248785 - Switch to Smart Window from the Switch Windows button
    """
    smart_window.open_window_switcher()
    smart_window.expect_switcher_selection("classic")
    smart_window.close_window_switcher()

    smart_window.click_switch_to_smart_window()

    # Sign-in is required first: the FxA flow opens in a new tab on the FxA
    # host the suite points Firefox at, tagged with the Smart Window entrypoint.
    fxa_host = urlparse(fxa_url).netloc if fxa_url else DEFAULT_FXA_HOST
    smart_window.expect_selected_tab_url_contains(fxa_host)
    smart_window.expect_selected_tab_url_contains("entrypoint=smartwindow")
    smart_window.expect_selected_tab_url_contains("service=smartwindow")

    # The window itself stays Classic until sign-in completes.
    smart_window.expect_smart_window_active(False)
