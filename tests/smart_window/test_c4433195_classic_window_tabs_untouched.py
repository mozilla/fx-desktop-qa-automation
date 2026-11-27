"""
C4433195 - Verify that the user cannot close tabs from a Classic window with Natural Language
Asking the Smart Window chat to close a tab that is open only in a Classic
window reports no match and leaves that tab open.
"""

import pytest
from auto_fxui.browser_object import SmartBar, SmartWindow, SmartWindowChat, TabBar
from auto_fxui.classes.recording import Recording, chat_reply, tool_call
from selenium.webdriver import Firefox

PROMPT = "Close my hotels tab"
REPLY = "I can't see a hotels tab in this window."
CLASSIC_PAGE = "hotels.html"


@pytest.fixture()
def test_case():
    return "4433195"


def test_classic_window_tabs_untouched(
    driver: Firefox,
    smart_window_chat: SmartWindowChat,
    smart_window: SmartWindow,
    built_replies: Recording,
    tab_pages,
):
    """
    C4433195 - Verify that the user cannot close tabs from a Classic window with Natural Language
    """
    classic_url = tab_pages([CLASSIC_PAGE])[0]
    built_replies.add(tool_call(PROMPT, "get_open_tabs", {}))
    built_replies.add(
        tool_call(
            PROMPT,
            "manage_tabs",
            {
                "action": "close_tabs",
                "ask_confirmation": False,
                "url_tokens": [classic_url],
            },
            tool_results=1,
        )
    )
    built_replies.add(chat_reply(PROMPT, REPLY, tool_results=2))

    tabs = TabBar(driver)
    chat = smart_window_chat
    smart_handle = driver.current_window_handle
    tabs.open_window_with_url(classic_url)
    smart_window.switch_to_classic_window()
    driver.switch_to.window(smart_handle)
    SmartBar(driver).open_full_page_chat()

    windows = smart_window.get_windows()
    assert [w["smart"] for w in windows].count(False) == 1, windows

    chat.send(PROMPT)

    results = chat.get_tool_results("manage_tabs")
    assert len(results) == 1 and "match" in str(results[0]).lower(), results
    assert chat.get_tool_ui_types() == []
    assert classic_url in [url for w in smart_window.get_windows() for url in w["urls"]]
