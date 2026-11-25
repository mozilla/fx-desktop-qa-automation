"""
C4516867 - Verify that the user can select the Dont learn from any activity option during Onboarding
Choosing Don't learn from any activity on the onboarding page leaves both
Learn from chats and Learn from browsing unchecked on the Personalize Smart
Window settings page.
"""

import pytest
from auto_fxui.browser_object import SmartWindow
from auto_fxui.page_object import AboutPrefs, SmartWindowFirstRun
from selenium.webdriver import Firefox


@pytest.fixture()
def test_case():
    return "4516867"


@pytest.fixture()
def fxa_env():
    return None


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.smartwindow.firstrun.hasCompleted", False),
        ("browser.smartwindow.firstrun.modelChoice", ""),
    ]


def test_dont_learn_from_activity_from_onboarding(
    driver: Firefox, active_smart_window: SmartWindow
):
    """
    C4516867 - Verify that the user can select the Dont learn from any activity option during Onboarding
    """
    smart_window = active_smart_window
    first_run = SmartWindowFirstRun(driver)
    about_prefs = AboutPrefs(driver, category="personalizeSmartWindow")

    smart_window.open_first_run()
    assert first_run.is_single_page(), "Expected the single-page onboarding"
    first_run.select_memories("none")
    assert first_run.get_selected_memories() == "none"
    assert (
        first_run.get_memories_button_label_id()
        == "smartwindow-onboarding-memories-none"
    )
    first_run.save()
    smart_window.expect_first_run_view(False)

    about_prefs.navigate_to_smart_window_settings(verify=False)
    about_prefs.element_visible("smart-window-learn-from-browsing-checkbox")
    about_prefs.expect(
        lambda _: (
            about_prefs.get_smart_window_memory_settings()
            == {"chats": False, "browsing": False}
        )
    )
