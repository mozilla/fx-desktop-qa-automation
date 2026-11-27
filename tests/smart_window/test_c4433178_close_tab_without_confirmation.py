"""
C4433178 - Verify that the AI model can close a Tab using Natural Language
Asking to close one background tab, with no confirmation requested, closes it
without showing a confirmation card.
"""

import pytest
from auto_fxui.browser_object import SmartBar, SmartWindowChat, TabBar
from auto_fxui.classes.recording import Recording, tool_call
from selenium.webdriver import Firefox

PROMPT = "Close my flights tab"
PAGES = ["lasagna.html", "flights.html", "hotels.html"]
CLOSED = ["flights.html"]


@pytest.fixture()
def test_case():
    return "4433178"


def test_close_tab_without_confirmation(
    driver: Firefox,
    smart_window_chat: SmartWindowChat,
    built_replies: Recording,
    tab_pages,
):
    """
    C4433178 - Verify that the AI model can close a Tab using Natural Language
    """
    built_replies.add(tool_call(PROMPT, "get_open_tabs", {}))
    built_replies.add(
        tool_call(
            PROMPT,
            "manage_tabs",
            {
                "action": "close_tabs",
                "ask_confirmation": False,
                "url_tokens": [SmartWindowChat.url_token(page) for page in CLOSED],
            },
            tool_results=1,
        )
    )

    tabs = TabBar(driver)
    chat = smart_window_chat
    tabs.open_urls_in_tabs(tab_pages(PAGES), open_first_in_current_tab=True)
    SmartBar(driver).open_full_page_chat()

    chat.send(PROMPT)

    tabs.expect_tabs_closed(tab_pages(CLOSED))
    assert chat.get_tool_ui_types() == ["ai-action-result"], (
        "Firefox showed a confirmation card"
    )
    tabs.expect_tabs_open(tab_pages(["lasagna.html", "hotels.html"]))
