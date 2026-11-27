"""
C3349900 - Verify that the Onboarding entry points and flowthrough are keyboard accessible
Signed out, the Switch Windows button and the Hamburger menu's New Smart
Window entry each start the sign-in that leads to onboarding when used with
the keyboard alone, and onboarding can then be finished the same way.
"""

import pytest
from auto_fxui.browser_object import SmartWindow
from auto_fxui.classes.fxa_session import FxaSession
from auto_fxui.page_object import FxaHome, SmartWindowFirstRun
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

NEW_SMART_WINDOW = "appMenu-new-ai-window-button"


@pytest.fixture()
def test_case():
    return "3349900"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.smartwindow.firstrun.hasCompleted", False),
        ("browser.smartwindow.firstrun.modelChoice", ""),
    ]


def test_onboarding_entry_points_keyboard_accessible(
    driver: Firefox, create_fxa: FxaSession, smart_window: SmartWindow
):
    """
    C3349900 - Verify that the Onboarding entry points and flowthrough are keyboard accessible
    """
    first_run = SmartWindowFirstRun(driver)

    num_tabs = len(driver.window_handles)
    smart_window.choose_window_with_keyboard("smart")
    smart_window.wait_for_num_tabs(num_tabs + 1)
    smart_window.switch_to_new_tab()
    smart_window.expect_selected_tab_url_contains("entrypoint=smartwindow")

    # Signed out, this opens a new window with its own sign-in tab.
    existing_count = len(driver.window_handles)
    smart_window.open_app_menu_with_keyboard()
    smart_window.choose_app_menu_item_with_keyboard(NEW_SMART_WINDOW)
    smart_window.wait_for_num_windows(existing_count + 2)
    smart_window.switch_to_new_tab()
    smart_window.expect_selected_tab_url_contains("entrypoint=smartwindow")

    fxa = FxaHome(driver)
    fxa.inject_session(create_fxa)
    fxa.continue_with_cached_account()
    smart_window.expect_signed_in()
    smart_window.expect_smart_window_active(True)
    smart_window.expect_first_run_view(True)
    smart_window.expect_selected_tab_url_contains("aiwindow/firstrun.html")

    assert first_run.is_single_page(), "Expected the single-page onboarding"
    first_run.tab_to_control("save")
    first_run.perform_key_combo(Keys.ENTER)

    smart_window.expect_first_run_view(False)
    smart_window.expect_selected_tab_url_contains("aiwindow/aiWindow.html")
    assert first_run.get_pref("browser.smartwindow.firstrun.hasCompleted") is True
