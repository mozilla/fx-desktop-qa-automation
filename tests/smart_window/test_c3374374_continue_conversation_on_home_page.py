"""
C3374374 - Continue a conversation on the Home page
"""

import pytest
from auto_fxui.browser_object import SmartBar, SmartWindowChat
from auto_fxui.classes.recording import Recording, chat_reply
from auto_fxui.mock_server import MockServer
from selenium.webdriver import Firefox

PROMPT = "In one plain sentence with no formatting, what is evolution?"
FOLLOW_UP = "In one plain sentence with no formatting, who described it first?"
REPLY = "Evolution is the change in heritable traits of populations over generations."
FOLLOW_UP_REPLY = "Charles Darwin described it first, in On the Origin of Species."


@pytest.fixture()
def test_case():
    return "3374374"


def test_continue_conversation_on_home_page(
    driver: Firefox, smart_window_chat: SmartWindowChat, mock_server: MockServer
):
    """
    C3374374 - Continue a conversation on the Home page
    """
    # Hand-built: only the reply text matters, so a recording would add nothing.
    mock_server.reset(
        Recording([chat_reply(PROMPT, REPLY), chat_reply(FOLLOW_UP, FOLLOW_UP_REPLY)])
    )

    bar = SmartBar(driver)
    bar.open_full_page_chat()
    chat = smart_window_chat
    chat.send(PROMPT)

    # The case also switches tabs and back before continuing. Switching the
    # driver's handle away and back leaves the Smart Bar unreachable, so that
    # step is not covered here -- see the Partial coverage note on the case.

    chat.send(FOLLOW_UP)

    assert [(m["role"], m["text"]) for m in chat.get_messages()] == [
        ("user", PROMPT),
        ("assistant", REPLY),
        ("user", FOLLOW_UP),
        ("assistant", FOLLOW_UP_REPLY),
    ]
