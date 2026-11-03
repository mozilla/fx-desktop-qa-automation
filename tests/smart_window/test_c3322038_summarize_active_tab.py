"""
C3322038 - Summarize the page for the active tab
"""

import pytest
from auto_fxui.browser_object import SmartBar, SmartWindow, SmartWindowChat
from auto_fxui.classes.recording import Recording, chat_reply, tool_call
from auto_fxui.mock_server import MockServer
from selenium.webdriver import Firefox

URL = "https://www.mozilla.org/"
PROMPT = "In one plain sentence with no formatting, summarize this page."
SUMMARY = "The page introduces Mozilla and the Firefox browser."


@pytest.fixture()
def test_case():
    return "3322038"


def test_summarize_active_tab(
    driver: Firefox, smart_window_chat: SmartWindowChat, mock_server: MockServer
):
    """
    C3322038 - Summarize the page for the active tab
    """
    # Summarizing reads the tab through the get_page_content tool, so the reply
    # comes in two rounds: the tool call, then the summary once Firefox has
    # answered it.
    mock_server.reset(
        Recording(
            [
                tool_call(PROMPT, "get_page_content", {}),
                chat_reply(PROMPT, SUMMARY, tool_results=1),
            ]
        )
    )

    driver.get(URL)
    # The summary is of whatever tab is selected, so confirm the navigation
    # landed on a content tab rather than the Smart Window itself.
    SmartWindow(driver).expect_selected_tab_url_contains("mozilla.org")
    SmartBar(driver).open_smart_bar()

    chat = smart_window_chat
    chat.send(PROMPT)

    assert chat.get_last_reply() == SUMMARY
    # The reply text is canned, so it alone proves nothing. This checks
    # Firefox actually ran the tool round rather than answering without it.
    assert mock_server.tool_calls("get_page_content"), (
        "Firefox never ran the get_page_content round"
    )
