"""
C4438277 - Verify that the user can group related tabs
Asking the full-page chat to group the recipe tabs creates one tab group
holding exactly the recipe tabs.
"""

import pytest

from modules.browser_object import SmartBar, SmartWindowChat, TabBar
from modules.classes.tab_grouping_scenario import TabGroupingScenario
from modules.mock_server import MockServer

SCENARIO = TabGroupingScenario(
    instruction="Group my recipe tabs",
    pages=["lasagna.html", "cookie_recipe.html", "flights.html"],
    expected=["lasagna.html", "cookie_recipe.html"],
)


@pytest.fixture()
def test_case():
    return "4438277"


def test_group_related_tabs(
    smart_window_chat: SmartWindowChat, mock_server: MockServer, tab_pages, driver
):
    """
    C4438277 - Verify that the user can group related tabs
    """
    tabs = TabBar(driver)
    tabs.open_urls_in_tabs(tab_pages(SCENARIO.pages), open_first_in_current_tab=True)

    SmartBar(driver).open_full_page_chat()

    chat = smart_window_chat
    chat.send(SCENARIO.instruction)
    manage_tabs = mock_server.tool_calls("manage_tabs")
    assert manage_tabs, "The model never called manage_tabs"

    chat.confirm_tab_grouping_if_asked()
    tabs.expect_tab_group_exists()

    # The model can call manage_tabs more than once in a turn (to retry, or
    # group then rename); the last call is the one whose result is on screen.
    last_request = manage_tabs[-1]
    SCENARIO.check_grouping(
        tabs.get_tab_groups(),
        chat.resolve_url_tokens(last_request["url_tokens"]),
    )
