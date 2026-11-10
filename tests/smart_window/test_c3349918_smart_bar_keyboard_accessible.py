"""
C3349918 - Verify that the Smart bar is keyboard accessible
In a new tab opened with the keyboard, the Smart Bar has focus, Tab reaches
every Smart Bar button, and each Go/Ask action can be chosen with the keyboard.
"""

import pytest
from auto_fxui.browser_object import SmartBar, SmartWindow, TabBar
from auto_fxui.browser_object_smart_bar import (
    ACTION_MENU_CHAT,
    ACTION_MENU_GO_TO_SITE,
    ACTION_MENU_SEARCH_WITH_DEFAULT,
)
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

# A domain, so the menu offers Go to site as well as Ask and Search.
QUERY = "example.com"
ACTIONS = {
    ACTION_MENU_CHAT: "chat",
    ACTION_MENU_SEARCH_WITH_DEFAULT: "search",
    ACTION_MENU_GO_TO_SITE: "navigate",
}


@pytest.fixture()
def test_case():
    return "3349918"


def test_smart_bar_keyboard_accessible(
    driver: Firefox, active_smart_window: SmartWindow, sys_platform: str
):
    """
    C3349918 - Verify that the Smart bar is keyboard accessible
    """
    # Instantiate objects
    tabs = TabBar(driver)
    smart_bar = SmartBar(driver)

    with driver.context(driver.CONTEXT_CHROME):
        tabs.new_tab_by_keys(sys_platform)
    smart_bar.expect_smart_bar_ready()
    smart_bar.expect(lambda _: smart_bar.is_editor_focused())

    # Before typing, so Tab doesn't first step through suggestions.
    for name in ("context", "memories", "model"):
        smart_bar.tab_to_button(name)
    smart_bar.press(Keys.ENTER)
    # The menu takes focus once it has opened; Escape before that is lost.
    smart_bar.expect(lambda _: smart_bar.model_menu_has_focus())
    smart_bar.press(Keys.ESCAPE)
    smart_bar.expect(lambda _: not smart_bar.is_model_menu_open())

    smart_bar.set_smart_bar_text(QUERY)
    smart_bar.tab_to_button("cta")
    for item, action in ACTIONS.items():
        smart_bar.choose_action_with_keyboard(item)
        assert smart_bar.get_action() == action, f"{item} didn't set {action}"
