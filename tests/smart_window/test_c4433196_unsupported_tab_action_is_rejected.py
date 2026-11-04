"""
C4433196 - Verify that an unsupported tab action name is rejected
When the model asks manage_tabs for an action Firefox doesn't have, Firefox
tells the model so and leaves the tabs alone.
"""

import pytest
from auto_fxui.browser_object import SmartBar, SmartWindowChat, TabBar
from auto_fxui.classes.recording import Recording, tool_call

PROMPT = "Explode my lasagna tab"
PAGES = ["lasagna.html", "flights.html"]
LASAGNA_TOKEN = "§url_token: LOCALHOST_LASAGNA_HTML_1§"
ACTION = "explode_tabs"


@pytest.fixture()
def test_case():
    return "4433196"


def test_unsupported_tab_action_is_rejected(
    smart_window_chat: SmartWindowChat, built_replies: Recording, tab_pages, driver
):
    """
    C4433196 - Verify that an unsupported tab action name is rejected
    """
    # get_open_tabs runs first so manage_tabs names a real tab; only the action is wrong.
    built_replies.add(tool_call(PROMPT, "get_open_tabs", {}))
    built_replies.add(
        tool_call(
            PROMPT,
            "manage_tabs",
            {
                "action": ACTION,
                "ask_confirmation": False,
                "url_tokens": [LASAGNA_TOKEN],
            },
            tool_results=1,
        )
    )

    # Instantiate objects
    tabs = TabBar(driver)
    tabs.open_urls_in_tabs(tab_pages(PAGES), open_first_in_current_tab=True)

    SmartBar(driver).open_full_page_chat()
    open_tabs = tabs.get_tab_urls()

    chat = smart_window_chat
    chat.send(PROMPT)

    results = chat.get_tool_results("manage_tabs")
    assert len(results) == 1 and ACTION in str(results[0]), (
        f"Firefox didn't reject {ACTION}: {results}"
    )
    assert chat.get_tool_ui_types() == [], "Firefox showed a card for the action"
    assert tabs.get_tab_urls() == open_tabs
    assert tabs.get_tab_groups() == []
