"""
C3374375 - Verify that the user can continue the conversation in the Chat Sidebar
"""

import pytest

from modules.browser_object import SmartBar, SmartWindowChat
from modules.mock_server import MockServer

PROMPT = "In one plain sentence with no formatting, what is a group of otters called?"


@pytest.fixture()
def test_case():
    return "3374375"


def test_continue_conversation_in_sidebar(
    smart_window_chat: SmartWindowChat, mock_server: MockServer, driver
):
    """
    C3374375 - Verify that the user can continue the conversation in the Chat Sidebar
    """
    SmartBar(driver).open_smart_bar()
    chat = smart_window_chat
    chat.send(PROMPT)

    shown = [(m["role"], m["text"]) for m in chat.get_messages()]
    assert shown == [
        ("user", PROMPT),
        ("assistant", mock_server.chat_reply_text(PROMPT)),
    ]
