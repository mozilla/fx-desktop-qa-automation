"""
C3371299 - Verify that the user can start the Onboarding process from the
Hamburger menu
Signed out, "New Smart Window" in the Hamburger menu opens FxA sign-in; after
signing in, the AI model page is shown, and choosing a model opens the Smart
Window home page.
"""

import pytest
from auto_fxui.browser_object import PanelUi, SmartWindow
from auto_fxui.classes.fxa_session import FxaSession
from auto_fxui.page_object import FxaHome, SmartWindowFirstRun


@pytest.fixture()
def test_case():
    return "3371299"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.smartwindow.firstrun.hasCompleted", False),
        ("browser.smartwindow.firstrun.modelChoice", ""),
    ]


def test_onboarding_from_hamburger_menu(
    driver, create_fxa: FxaSession, smart_window: SmartWindow
):
    """
    C3371299 - Verify that the user can start the Onboarding process from the
    Hamburger menu
    """
    # Instantiate objects
    panel_ui = PanelUi(driver)
    fxa = FxaHome(driver)
    first_run = SmartWindowFirstRun(driver)

    panel_ui.open_panel_menu()
    panel_ui.element_visible("panel-ui-new-smart-window")
    existing_count = len(driver.window_handles)
    panel_ui.click_on("panel-ui-new-smart-window")

    # Signed out, Firefox opens a new window and an FxA sign-in tab in it.
    smart_window.wait_for_num_windows(existing_count + 2)
    smart_window.switch_to_new_tab()
    smart_window.expect_selected_tab_url_contains("entrypoint=smartwindow")

    fxa.inject_session(create_fxa)
    fxa.continue_with_cached_account()
    smart_window.expect_signed_in()

    # Once signed in, the new window turns Smart and starts onboarding.
    smart_window.expect_smart_window_active(True)
    smart_window.expect_first_run_view(True)
    smart_window.expect_selected_tab_url_contains("aiwindow/firstrun.html")

    # Any offered model: this case is about starting onboarding, not a model.
    first_run.complete_onboarding()

    # Onboarding ends on the Smart Window home page.
    smart_window.expect_first_run_view(False)
    smart_window.expect_selected_tab_url_contains("aiwindow/aiWindow.html")
    first_run.expect_model_choice_saved()
    assert first_run.get_pref("browser.smartwindow.firstrun.hasCompleted") is True
