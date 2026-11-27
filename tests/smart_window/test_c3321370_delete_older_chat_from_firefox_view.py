"""
C3321370 - Verify that the user can delete older Chat entries from the Firefox View page
Chats are listed by the date they were last updated, so two of the three are
backdated to count as older.
"""

import pytest
from auto_fxui.browser_object import SmartBar, SmartWindowChat
from auto_fxui.classes.recording import Recording, chat_reply
from auto_fxui.page_object_firefox_view import FirefoxView
from selenium.webdriver import Firefox

PROMPTS = ["Name a fruit", "Name a vegetable", "Name a grain"]
OLDER_BY_DAYS = 40


@pytest.fixture()
def test_case():
    return "3321370"


def test_delete_older_chat_from_firefox_view(
    smart_window_chat: SmartWindowChat, built_replies: Recording, driver: Firefox
):
    """
    C3321370 - Verify that the user can delete older Chat entries from the Firefox View page
    """
    for prompt in PROMPTS:
        built_replies.add(chat_reply(prompt, f"Answer to: {prompt}"))

    chat = smart_window_chat
    for i, prompt in enumerate(PROMPTS, start=1):
        SmartBar(driver).open_full_page_chat()
        chat.send(prompt)
        chat.expect_saved_conversations(i)

    recent, older_kept, older_deleted = chat.get_saved_conversation_ids()
    for conversation_id in (older_kept, older_deleted):
        chat.set_conversation_age(conversation_id, OLDER_BY_DAYS)

    fx_view = FirefoxView(driver)
    fx_view.open_chats()
    fx_view.expect_chats([recent, older_kept, older_deleted])

    fx_view.delete_chat(older_deleted)
    fx_view.expect_chat_gone(older_deleted)
    assert set(fx_view.get_chat_ids()) == {recent, older_kept}
    assert older_deleted not in chat.get_saved_conversation_ids()
