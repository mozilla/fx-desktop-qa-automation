"""
C4433183 - Verify that the AI model returns an error when there is no match for which tab to close
When the model asks to close a URL no tab shows, Firefox sends a no-match
error back to the model, shows no card and closes nothing.
"""

import pytest
from auto_fxui.browser_object import SmartBar, SmartWindowChat, TabBar
from auto_fxui.classes.recording import Recording, chat_reply, tool_call
from selenium.webdriver import Firefox

PROMPT = "Close my weather tab"
PAGES = ["lasagna.html", "flights.html"]
MISSING_URL = "https://example.com/weather"
REPLY = "I couldn't find a weather tab."


@pytest.fixture()
def test_case():
    return "4433183"


def test_close_tab_with_no_match(
    driver: Firefox,
    smart_window_chat: SmartWindowChat,
    built_replies: Recording,
    tab_pages,
):
    """
    C4433183 - Verify that the AI model returns an error when there is no match for which tab to close
    """
    built_replies.add(tool_call(PROMPT, "get_open_tabs", {}))
    built_replies.add(
        tool_call(
            PROMPT,
            "manage_tabs",
            {
                "action": "close_tabs",
                "ask_confirmation": False,
                "url_tokens": [MISSING_URL],
            },
            tool_results=1,
        )
    )
    built_replies.add(chat_reply(PROMPT, REPLY, tool_results=2))

    tabs = TabBar(driver)
    chat = smart_window_chat
    tabs.open_urls_in_tabs(tab_pages(PAGES), open_first_in_current_tab=True)
    SmartBar(driver).open_full_page_chat()
    open_tabs = tabs.get_tab_urls()

    chat.send(PROMPT)

    results = chat.get_tool_results("manage_tabs")
    assert len(results) == 1 and "match" in str(results[0]).lower(), (
        f"Firefox didn't report a missing tab: {results}"
    )
    assert chat.get_last_reply() == REPLY
    assert chat.get_tool_ui_types() == [], "Firefox showed a card"
    assert tabs.get_tab_urls() == open_tabs
