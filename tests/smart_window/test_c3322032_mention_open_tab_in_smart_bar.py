"""
C3322032 - Verify that the user can @ an opened tab inside the Smart bar
Typing @ in the Smart Bar lists the open tab; choosing it adds the tab inline,
and the assistant is asked about that tab.
"""

import pytest
from auto_fxui.browser_object import SmartBar, SmartWindowChat, TabBar
from auto_fxui.classes.recording import Recording, chat_reply
from selenium.webdriver import Firefox

TAB_TITLE = "The Very Best Lasagna Recipe"
# Firefox sends a mention to the model as a link to the tab's URL token.
PROMPT = f"Summarize [{TAB_TITLE}](§url_token: LOCALHOST_LASAGNA_HTML_1§)"
SUMMARY = "The page is a recipe for a classic baked lasagna."


@pytest.fixture()
def test_case():
    return "3322032"


def test_mention_open_tab_in_smart_bar(
    driver: Firefox,
    smart_window_chat: SmartWindowChat,
    built_replies: Recording,
    tab_pages,
):
    """
    C3322032 - Verify that the user can @ an opened tab inside the Smart bar
    """
    built_replies.add(chat_reply(PROMPT, SUMMARY))

    tabs = TabBar(driver)
    smart_bar = SmartBar(driver)
    chat = smart_window_chat

    tab_url = tab_pages(["lasagna.html"])[0]
    tabs.open_urls_in_tabs([tab_url], open_first_in_current_tab=True)
    smart_bar.open_full_page_chat()

    smart_bar.set_smart_bar_text("Summarize ")
    smart_bar.type_mention_trigger()
    suggestions = [s["title"] for s in smart_bar.get_mention_suggestions()]
    assert TAB_TITLE in suggestions, f"The open tab wasn't suggested: {suggestions}"

    smart_bar.choose_mention(tab_url)
    assert smart_bar.get_inline_mentions() == [TAB_TITLE]

    chat.send_typed()
    assert chat.get_last_reply() == SUMMARY
