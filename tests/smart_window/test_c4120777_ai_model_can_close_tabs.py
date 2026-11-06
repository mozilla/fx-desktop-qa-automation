"""
C4120777 - Verify that the AI model can close tabs
Asking the full-page chat to close the recipe tabs closes them and leaves
the other tab open.
"""

import pytest
from auto_fxui.browser_object import SmartBar, SmartWindowChat, TabBar
from auto_fxui.classes.tab_grouping_scenario import CHAT_TAB_URL
from auto_fxui.mock_server import MockServer

INSTRUCTION = "Close my recipe tabs"
PAGES = ["lasagna.html", "cookie_recipe.html", "flights.html"]
EXPECTED_OPEN = ["flights.html"]


@pytest.fixture()
def test_case():
    return "4120777"


def test_ai_model_can_close_tabs(
    smart_window_chat: SmartWindowChat, mock_server: MockServer, tab_pages, driver
):
    """
    C4120777 - Verify that the AI model can close tabs
    """
    # Instantiate objects
    tabs = TabBar(driver)
    tabs.open_urls_in_tabs(tab_pages(PAGES), open_first_in_current_tab=True)

    SmartBar(driver).open_full_page_chat()

    chat = smart_window_chat
    chat.send(INSTRUCTION)
    manage_tabs = mock_server.tool_calls("manage_tabs")
    assert manage_tabs, "The model never called manage_tabs"
    last_request = manage_tabs[-1]
    assert last_request["action"] == "close_tabs", last_request

    chat.confirm_tab_action_if_asked()

    tabs.expect_tabs_closed(chat.resolve_url_tokens(last_request["url_tokens"]))
    still_open = [
        url.rsplit("/", 1)[-1] for url in tabs.get_tab_urls() if url != CHAT_TAB_URL
    ]
    assert still_open == EXPECTED_OPEN, f"The model left {still_open} open"
