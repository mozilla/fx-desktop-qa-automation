"""
C4120780 - Verify that the user can Cancel Closing tabs
With the close-tabs card waiting, closing it or sending another prompt
cancels the request and closes nothing.
"""

import pytest
from auto_fxui.browser_object import SmartBar, SmartWindowChat, TabBar
from auto_fxui.classes.recording import Recording, chat_reply, tool_call
from selenium.webdriver import Firefox

PROMPT = "Close all my other tabs"
NEXT_PROMPT = "Never mind, what is a lasagna?"
NEXT_REPLY = "A lasagna is a layered pasta dish."
PAGES = ["lasagna.html", "cookie_recipe.html", "flights.html", "hotels.html"]


@pytest.fixture()
def test_case():
    return "4120780"


@pytest.mark.parametrize("how", ["close_button", "new_prompt"])
def test_cancel_closing_tabs(
    driver: Firefox,
    smart_window_chat: SmartWindowChat,
    built_replies: Recording,
    tab_pages,
    how: str,
):
    """
    C4120780 - Verify that the user can Cancel Closing tabs
    """
    built_replies.add(tool_call(PROMPT, "get_open_tabs", {}))
    built_replies.add(
        tool_call(
            PROMPT,
            "manage_tabs",
            {
                "action": "close_tabs",
                "ask_confirmation": True,
                "url_tokens": [SmartWindowChat.url_token(page) for page in PAGES],
            },
            tool_results=1,
        )
    )
    built_replies.add(chat_reply(NEXT_PROMPT, NEXT_REPLY, tool_results=2))

    tabs = TabBar(driver)
    chat = smart_window_chat
    urls = tab_pages(PAGES)
    tabs.open_urls_in_tabs(urls, open_first_in_current_tab=True)
    SmartBar(driver).open_full_page_chat()

    chat.send(PROMPT)
    assert chat.get_last_tool_ui_type() == "website-confirmation"

    if how == "close_button":
        chat.cancel_confirmation()
    else:
        chat.send(NEXT_PROMPT)
    chat.expect_cancelled()

    tabs.expect_tabs_open(urls)
