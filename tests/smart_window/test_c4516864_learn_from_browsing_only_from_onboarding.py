"""
C4516864 - Verify that the user can Personalize how Smart window learns about you from the Onboarding page
Choosing Browsing only on the onboarding page leaves only Learn from browsing
checked on the Personalize Smart Window settings page.
"""

import pytest
from auto_fxui.browser_object import SmartWindow
from auto_fxui.page_object import AboutPrefs, SmartWindowFirstRun
from selenium.webdriver import Firefox


@pytest.fixture()
def test_case():
    return "4516864"


@pytest.fixture()
def fxa_env():
    return None


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.smartwindow.firstrun.hasCompleted", False),
        ("browser.smartwindow.firstrun.modelChoice", ""),
    ]


def test_learn_from_browsing_only_from_onboarding(
    driver: Firefox, active_smart_window: SmartWindow
):
    """
    C4516864 - Verify that the user can Personalize how Smart window learns about you from the Onboarding page
    """
    smart_window = active_smart_window
    first_run = SmartWindowFirstRun(driver)
    about_prefs = AboutPrefs(driver, category="personalizeSmartWindow")

    smart_window.open_first_run()
    assert first_run.is_single_page(), "Expected the single-page onboarding"
    first_run.select_memories("browsing")
    assert first_run.get_selected_memories() == "browsing"
    assert (
        first_run.get_memories_button_label_id()
        == "smartwindow-onboarding-memories-browsing"
    )
    first_run.save()
    smart_window.expect_first_run_view(False)

    about_prefs.navigate_to_smart_window_settings(verify=False)
    about_prefs.element_visible("smart-window-learn-from-browsing-checkbox")
    about_prefs.expect(
        lambda _: (
            about_prefs.get_smart_window_memory_settings()
            == {"chats": False, "browsing": True}
        )
    )
