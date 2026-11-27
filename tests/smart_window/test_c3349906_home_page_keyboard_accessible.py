"""
C3349906 - Verify that the user can Reach the Homepage or New Tab null states using Keyboard Navigation
In a new tab opened with the keyboard, the Smart Bar has focus, Tab reaches
every prompt button, and Enter on a prompt sends it to the assistant.
"""

import pytest
from auto_fxui.browser_object import SmartBar, SmartWindowChat, TabBar
from auto_fxui.classes.recording import Recording, chat_reply
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

REPLY = "Here is a start."


@pytest.fixture()
def test_case():
    return "3349906"


def test_home_page_keyboard_accessible(
    driver: Firefox,
    smart_window_chat: SmartWindowChat,
    built_replies: Recording,
    sys_platform: str,
):
    """
    C3349906 - Verify that the user can Reach the Homepage or New Tab null states using Keyboard Navigation
    """
    tabs = TabBar(driver)
    smart_bar = SmartBar(driver)
    chat = smart_window_chat

    with driver.context(driver.CONTEXT_CHROME):
        tabs.new_tab_by_keys(sys_platform)
    smart_bar.expect_smart_bar_ready()
    smart_bar.expect(lambda _: smart_bar.is_editor_focused())

    labels = smart_bar.get_home_prompt_labels()
    assert labels, "The Home page shows no prompt buttons"
    for index in range(len(labels)):
        smart_bar.tab_to_home_prompt(index)
        assert smart_bar.get_focused_home_prompt() == index

    # The prompts change from visit to visit, so the reply is built for the one used.
    prompt = labels[-1]
    built_replies.add(chat_reply(prompt, REPLY))
    smart_bar.perform_key_combo_chrome(Keys.ENTER)
    chat.expect_turn_complete(1)
    assert chat.get_last_reply() == REPLY
    assert chat.get_messages()[0]["text"] == prompt
