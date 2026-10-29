"""
C3322038 - Summarize the page for the active tab
"""

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import SmartBar, SmartWindowChat
from modules.classes.recording import Recording, chat_reply, tool_call
from modules.mock_server import MockServer

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
    SmartBar(driver).open_smart_bar()

    chat = smart_window_chat
    chat.send(PROMPT)

    assert chat.get_last_reply() == SUMMARY
    assert mock_server.tool_calls("get_page_content"), (
        "the assistant never called get_page_content, so the tab was not read"
    )
