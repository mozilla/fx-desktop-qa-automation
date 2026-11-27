"""
Setup check for the uk_user fixture, with no TestRail case.
A UK user runs Firefox in en-GB with region GB, and chat requests carry en-GB.
"""

import pytest
from auto_fxui.browser_object import SmartBar, SmartWindowChat
from auto_fxui.classes.recording import Recording, chat_reply
from auto_fxui.locale_setup import get_locale_state
from auto_fxui.mock_server import MockServer

PROMPT = "What's the weather like today?"
REPLY = "Mild and cloudy."


@pytest.fixture()
def fxa_env():
    """No FxA: the WAF bypass is installed in the Firefox that restart() quits."""
    return None


@pytest.mark.usefixtures("uk_user")
def test_uk_user_setup(
    smart_window_chat: SmartWindowChat,
    built_replies: Recording,
    mock_server: MockServer,
    driver,
):
    built_replies.add(chat_reply(PROMPT, REPLY))

    state = get_locale_state(driver)
    assert state["appLocale"] == "en-GB", state
    assert state["region"] == "GB", state

    SmartBar(driver).open_full_page_chat()
    smart_window_chat.send(PROMPT)

    bodies = mock_server.request_bodies(purpose="chat")
    assert bodies, "Firefox sent no chat request"
    assert any("Locale: en-GB" in str(body) for body in bodies), (
        "No chat request body carries Locale: en-GB"
    )
