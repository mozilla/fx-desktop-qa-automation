"""
C4433184 - Verify that the AI model asks for confirmation when closing a Pinned tab
Asking to close a pinned tab with no confirmation requested still shows a
confirmation card and leaves the tab open until the user confirms.
"""

import pytest
from auto_fxui.browser_object import SmartBar, SmartWindowChat, TabBar
from auto_fxui.classes.recording import Recording, tool_call
from selenium.webdriver import Firefox

PROMPT = "Close my flights tab"
PAGES = ["flights.html", "lasagna.html", "hotels.html"]
PINNED = "flights.html"


@pytest.fixture()
def test_case():
    return "4433184"


def test_close_pinned_tab_needs_confirmation(
    driver: Firefox,
    smart_window_chat: SmartWindowChat,
    built_replies: Recording,
    tab_pages,
):
    """
    C4433184 - Verify that the AI model asks for confirmation when closing a Pinned tab
    """
    built_replies.add(tool_call(PROMPT, "get_open_tabs", {}))
    built_replies.add(
        tool_call(
            PROMPT,
            "manage_tabs",
            {
                "action": "close_tabs",
                "ask_confirmation": False,
                "url_tokens": [SmartWindowChat.url_token(PINNED)],
            },
            tool_results=1,
        )
    )

    tabs = TabBar(driver)
    chat = smart_window_chat
    pinned_url = tab_pages([PINNED])[0]
    tabs.open_urls_in_tabs(tab_pages(PAGES), open_first_in_current_tab=True)
    tabs.pin_tab(pinned_url)
    SmartBar(driver).open_full_page_chat()

    chat.send(PROMPT)

    assert chat.get_last_tool_ui_type() == "website-confirmation"
    assert pinned_url in tabs.get_tab_urls(), "The pinned tab closed unasked"

    chat.confirm_action()

    tabs.expect_tabs_closed([pinned_url])
