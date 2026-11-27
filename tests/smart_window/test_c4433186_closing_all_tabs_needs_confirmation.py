"""
C4433186 - Verify that a confirmation prompt is displayed when trying to close all tabs
Asking to close every tab with no confirmation requested shows a card listing
all of them and closes nothing until the user confirms.
"""

import pytest
from auto_fxui.browser_object import SmartBar, SmartWindowChat, TabBar
from auto_fxui.classes.recording import Recording, tool_call
from selenium.webdriver import Firefox

PROMPT = "Close all my tabs"
PAGES = [
    "lasagna.html",
    "cookie_recipe.html",
    "flights.html",
    "hotels.html",
    "museums.html",
]


@pytest.fixture()
def test_case():
    return "4433186"


def test_closing_all_tabs_needs_confirmation(
    driver: Firefox,
    smart_window_chat: SmartWindowChat,
    built_replies: Recording,
    tab_pages,
):
    """
    C4433186 - Verify that a confirmation prompt is displayed when trying to close all tabs
    """
    built_replies.add(tool_call(PROMPT, "get_open_tabs", {}))
    built_replies.add(
        tool_call(
            PROMPT,
            "manage_tabs",
            {
                "action": "close_tabs",
                "ask_confirmation": False,
                "url_tokens": [SmartWindowChat.url_token(page) for page in PAGES],
            },
            tool_results=1,
        )
    )

    tabs = TabBar(driver)
    chat = smart_window_chat
    urls = tab_pages(PAGES)
    tabs.open_urls_in_tabs(urls, open_first_in_current_tab=True)
    # The sidebar adds no tab, so the five pages are every tab in the window.
    SmartBar(driver).open_smart_bar()

    chat.send(PROMPT)

    assert chat.get_last_tool_ui_type() == "website-confirmation"
    assert len(chat.get_confirmation_tabs()) == len(PAGES)
    tabs.expect_tabs_open(urls)

    chat.confirm_action()

    tabs.expect_tabs_closed(urls)
