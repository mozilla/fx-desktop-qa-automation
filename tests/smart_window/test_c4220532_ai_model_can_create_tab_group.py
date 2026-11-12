"""
C4220532 - Verify that the AI model can create a tab group
Asking the full-page chat to group two named tabs creates one tab group
holding exactly those tabs.
"""

import pytest
from auto_fxui.browser_object import SmartBar, SmartWindowChat, TabBar
from auto_fxui.classes.tab_grouping_scenario import TabGroupingScenario
from auto_fxui.mock_server import MockServer

# Unlike C4438277, the tabs are named and unrelated, so this tests the group
# being created rather than the model deciding which tabs belong together.
SCENARIO = TabGroupingScenario(
    instruction="Create a tab group with my lasagna and flights tabs",
    pages=["lasagna.html", "cookie_recipe.html", "flights.html"],
    expected=["lasagna.html", "flights.html"],
)


@pytest.fixture()
def test_case():
    return "4220532"


def test_ai_model_can_create_tab_group(
    smart_window_chat: SmartWindowChat, mock_server: MockServer, tab_pages, driver
):
    """
    C4220532 - Verify that the AI model can create a tab group
    """
    # Instantiate objects
    tabs = TabBar(driver)
    tabs.open_urls_in_tabs(tab_pages(SCENARIO.pages), open_first_in_current_tab=True)

    SmartBar(driver).open_full_page_chat()

    chat = smart_window_chat
    chat.send(SCENARIO.instruction)
    manage_tabs = mock_server.tool_calls("manage_tabs")
    assert manage_tabs, "The model never called manage_tabs"
    last_request = manage_tabs[-1]
    assert last_request["action"] == "group_tabs", last_request

    chat.confirm_tab_action_if_asked()

    tabs.expect_tabs_grouped(chat.resolve_url_tokens(last_request["url_tokens"]))
    SCENARIO.check_grouping(tabs.get_tab_groups())
