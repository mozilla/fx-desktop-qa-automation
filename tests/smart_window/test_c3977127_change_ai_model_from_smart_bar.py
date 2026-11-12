"""
C3977127 - Verify that the user can change the AI model from the Smart Bar
The Smart Bar's model picker lists the three models; choosing Qwen closes the
picker, and the next message goes to Qwen.
"""

import pytest
from auto_fxui.browser_object import SmartBar, SmartWindowChat
from auto_fxui.classes.recording import Recording, chat_reply
from auto_fxui.mock_server import MockServer
from selenium.webdriver import Firefox

PROMPT = "In one sentence, which AI model are you?"
REPLY = "I'm an AI browsing assistant in Firefox's Smart Window, powered by Qwen."


@pytest.fixture()
def test_case():
    return "3977127"


def test_change_ai_model_from_smart_bar(
    driver: Firefox,
    smart_window_chat: SmartWindowChat,
    built_replies: Recording,
    mock_server: MockServer,
):
    """
    C3977127 - Verify that the user can change the AI model from the Smart Bar
    """
    built_replies.add(chat_reply(PROMPT, REPLY))

    smart_bar = SmartBar(driver)
    chat = smart_window_chat

    smart_bar.open_full_page_chat()
    models = smart_bar.get_models()
    assert smart_bar.get_selected_model() == models["Gemini"]

    smart_bar.open_model_menu()
    offered = smart_bar.get_model_menu_items()
    assert len(offered) == 3, f"Expected 3 models in the picker: {offered}"

    smart_bar.choose_model("Qwen")

    chat.send(PROMPT)
    assert chat.get_last_reply() == REPLY
    assert mock_server.chat_models(PROMPT) == [models["Qwen"]]
