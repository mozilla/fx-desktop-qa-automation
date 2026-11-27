"""
C3349912 - Verify that the Assistant CHAT sidebar is keyboard accessible
The sidebar opens from the Ask button with the keyboard, Tab reaches each of
its controls before and after a conversation, and they can be used with Enter.
"""

import pytest
from auto_fxui.browser_object import SmartBar, SmartWindow, SmartWindowChat
from auto_fxui.classes.recording import Recording, chat_reply
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

PROMPT = "What do otters eat?"
REPLY = "Mostly fish, plus crabs and frogs."
SMART_BAR_CONTROLS = ["context", "memories", "model", "cta", "cta-menu"]
CONVERSATION_CONTROLS = [
    "new-chat",
    "history",
    "close",
    "thumbs-up",
    "thumbs-down",
    "copy",
    "retry",
]


@pytest.fixture()
def test_case():
    return "3349912"


def test_chat_sidebar_keyboard_accessible(
    driver: Firefox,
    active_smart_window: SmartWindow,
    smart_window_chat: SmartWindowChat,
    built_replies: Recording,
):
    """
    C3349912 - Verify that the Assistant CHAT sidebar is keyboard accessible
    """
    built_replies.add(chat_reply(PROMPT, REPLY))
    smart_bar = SmartBar(driver)
    chat = smart_window_chat

    active_smart_window.focus_toolbar_button("smartwindow-ask-button-inner")
    active_smart_window.perform_key_combo_chrome(Keys.ENTER)
    active_smart_window.expect_ai_sidebar_open(True)
    smart_bar.expect_smart_bar_ready()
    smart_bar.expect(lambda _: smart_bar.is_editor_focused())
    smart_bar.stub_intent_model("chat")

    chat.tab_through(SMART_BAR_CONTROLS)

    chat.focus_smart_bar()
    chat.type_with_keyboard(PROMPT)
    chat.perform_key_combo_chrome(Keys.ENTER)
    chat.expect_turn_complete(1)
    assert chat.get_last_reply() == REPLY

    chat.tab_through(CONVERSATION_CONTROLS)

    chat.tab_to_control("history")
    chat.perform_key_combo_chrome(Keys.ENTER)
    chat.expect(lambda _: chat.get_focused_control() != "history")
    chat.perform_key_combo_chrome(Keys.ESCAPE)
    chat.expect(lambda _: chat.get_focused_control() == "history")

    chat.tab_to_control("new-chat")
    chat.perform_key_combo_chrome(Keys.ENTER)
    chat.expect(lambda _: chat.get_messages() == [])

    chat.tab_to_control("close")
    chat.perform_key_combo_chrome(Keys.ENTER)
    active_smart_window.expect_ai_sidebar_open(False)
