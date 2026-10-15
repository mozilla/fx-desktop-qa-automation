"""
C3374375 - Verify that the user can continue the conversation in the Chat Sidebar
A follow-up message sent from the sidebar gets its own reply in the same
conversation, below the first exchange.
"""

import pytest

from modules.browser_object import SmartBar, SmartWindowChat
from modules.mock_server import MockServer

PROMPT = "In one plain sentence with no formatting, what is a group of otters called?"
FOLLOW_UP = (
    "Without searching the web, in one plain sentence with no formatting, "
    "what do they like to eat?"
)


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
    chat.send(FOLLOW_UP)

    # Both exchanges are shown, in order: the follow-up continued the
    # conversation rather than starting a new one.
    shown = [(m["role"], m["text"]) for m in chat.get_messages()]
    assert shown == [
        ("user", PROMPT),
        ("assistant", mock_server.chat_reply_text(PROMPT)),
        ("user", FOLLOW_UP),
        ("assistant", mock_server.chat_reply_text(FOLLOW_UP)),
    ]
