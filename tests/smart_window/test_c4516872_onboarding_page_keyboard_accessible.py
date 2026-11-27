"""
C4516872 - Verify that all the Onboarding page elements are keyboard accessible
On the single-page onboarding, the model and personalization dropdowns, the
Start in Smart Window toggle and the Let's go button all take focus from Tab
and can be used with Enter and Space.
"""

import pytest
from auto_fxui.browser_object import SmartWindow
from auto_fxui.page_object import SmartWindowFirstRun
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys


@pytest.fixture()
def test_case():
    return "4516872"


@pytest.fixture()
def fxa_env():
    return None


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.smartwindow.firstrun.hasCompleted", False),
        ("browser.smartwindow.firstrun.modelChoice", ""),
    ]


def test_onboarding_page_keyboard_accessible(
    driver: Firefox, active_smart_window: SmartWindow
):
    """
    C4516872 - Verify that all the Onboarding page elements are keyboard accessible
    """
    smart_window = active_smart_window
    first_run = SmartWindowFirstRun(driver)

    smart_window.open_first_run()
    assert first_run.is_single_page(), "Expected the single-page onboarding"
    first_run.expect_setup_screen()

    first_run.tab_to_control("model")
    first_run.model_choice_id = first_run.choose_other_option_with_keyboard("model")

    first_run.tab_to_control("memories")
    first_run.choose_other_option_with_keyboard("memories")

    first_run.tab_to_control("default-window")
    was_on = first_run.is_default_window_on()
    first_run.perform_key_combo(Keys.SPACE)
    first_run.expect(lambda _: first_run.is_default_window_on() != was_on)
    first_run.perform_key_combo(Keys.SPACE)
    first_run.expect(lambda _: first_run.is_default_window_on() == was_on)

    first_run.tab_to_control("save")
    first_run.perform_key_combo(Keys.ENTER)

    smart_window.expect_first_run_view(False)
    first_run.expect_model_choice_saved()
