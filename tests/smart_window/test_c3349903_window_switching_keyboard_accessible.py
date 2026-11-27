"""
C3349903 - Verify that the Window Switching Entry points are keyboard accessible
Signed in, the Switch Windows button and the New Smart Window entry in the
Hamburger menu can be reached and used with the keyboard alone.
"""

import pytest
from auto_fxui.browser_object import SmartWindow
from auto_fxui.classes.fxa_session import FxaSession
from auto_fxui.page_object import FxaHome
from selenium.webdriver import Firefox

NEW_SMART_WINDOW = "appMenu-new-ai-window-button"


@pytest.fixture()
def test_case():
    return "3349903"


def test_window_switching_keyboard_accessible(
    driver: Firefox, create_fxa: FxaSession, smart_window: SmartWindow
):
    """
    C3349903 - Verify that the Window Switching Entry points are keyboard accessible
    """
    smart_window.open_smart_window_sign_in()
    fxa = FxaHome(driver)
    fxa.inject_session(create_fxa)
    fxa.continue_with_cached_account()
    smart_window.expect_signed_in()
    smart_window.expect_smart_window_active(True)

    smart_window.choose_window_with_keyboard("classic")
    smart_window.expect_smart_window_active(False)

    smart_window.choose_window_with_keyboard("smart")
    smart_window.expect_smart_window_active(True)

    smart_window.choose_window_with_keyboard("classic")
    smart_window.expect_smart_window_active(False)

    existing_count = len(driver.window_handles)
    smart_window.open_app_menu_with_keyboard()
    smart_window.choose_app_menu_item_with_keyboard(NEW_SMART_WINDOW)
    smart_window.wait_for_num_windows(existing_count + 1)
    smart_window.switch_to_new_window()
    smart_window.expect_smart_window_active(True)
