"""
C4513494 - Verify that the user can select an AI model from the Onboarding page
The model picked on the single-page onboarding is the one the Smart Bar
shows once onboarding ends.
"""

import pytest
from auto_fxui.browser_object import SmartBar, SmartWindow
from auto_fxui.page_object import SmartWindowFirstRun
from selenium.webdriver import Firefox


@pytest.fixture()
def test_case():
    return "4513494"


@pytest.fixture()
def fxa_env():
    return None


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.smartwindow.firstrun.hasCompleted", False),
        ("browser.smartwindow.firstrun.modelChoice", ""),
    ]


def test_select_ai_model_during_onboarding(
    driver: Firefox, active_smart_window: SmartWindow
):
    """
    C4513494 - Verify that the user can select an AI model from the Onboarding page
    """
    smart_window = active_smart_window
    first_run = SmartWindowFirstRun(driver)
    smart_bar = SmartBar(driver)

    smart_window.open_first_run()
    assert first_run.is_single_page(), "Expected the single-page onboarding"

    # Any model other than the preselected one, so the choice is the user's.
    preselected = first_run.get_selected_model()
    model = next(m for m in first_run.get_offered_models() if m != preselected)
    first_run.select_model(model)
    assert first_run.get_selected_model() == model
    first_run.save()

    smart_window.expect_first_run_view(False)
    smart_window.expect_selected_tab_url_contains("aiwindow/aiWindow.html")
    first_run.expect_model_choice_saved()

    smart_bar.expect_smart_bar_ready()
    assert smart_bar.get_selected_model() == smart_bar.get_models()[model]
