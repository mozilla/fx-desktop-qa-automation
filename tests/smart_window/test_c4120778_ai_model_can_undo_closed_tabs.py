"""
C4120778 - Verify that the AI model can Undo Closed tabs
After the assistant closes two of five tabs and the user confirms, Undo on the
result card reopens both.
"""

import pytest
from auto_fxui.browser_object import SmartBar, SmartWindowChat, TabBar
from auto_fxui.classes.recording import Recording, tool_call
from selenium.webdriver import Firefox

PROMPT = "Close my recipe tabs"
PAGES = [
    "lasagna.html",
    "cookie_recipe.html",
    "flights.html",
    "hotels.html",
    "museums.html",
]
CLOSED = ["lasagna.html", "cookie_recipe.html"]


def url_token(page: str) -> str:
    """Return the URL token the model names a tab served from `page` by."""
    return f"§url_token: LOCALHOST_{page.upper().replace('.', '_')}_1§"


@pytest.fixture()
def test_case():
    return "4120778"


def test_ai_model_can_undo_closed_tabs(
    driver: Firefox,
    smart_window_chat: SmartWindowChat,
    built_replies: Recording,
    tab_pages,
):
    """
    C4120778 - Verify that the AI model can Undo Closed tabs
    """
    built_replies.add(tool_call(PROMPT, "get_open_tabs", {}))
    built_replies.add(
        tool_call(
            PROMPT,
            "manage_tabs",
            {
                "action": "close_tabs",
                "ask_confirmation": True,
                "url_tokens": [url_token(page) for page in CLOSED],
            },
            tool_results=1,
        )
    )

    tabs = TabBar(driver)
    chat = smart_window_chat
    urls = tab_pages(PAGES)
    closed_urls = tab_pages(CLOSED)

    tabs.open_urls_in_tabs(urls, open_first_in_current_tab=True)
    SmartBar(driver).open_full_page_chat()

    chat.send(PROMPT)
    chat.confirm_tab_action_if_asked()
    tabs.expect_tabs_closed(closed_urls)

    chat.undo_last_action()
    tabs.expect_tabs_open(urls)
