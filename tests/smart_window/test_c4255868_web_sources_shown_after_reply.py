"""
C4255868 - Verify that Exa search sources are displayed inline when multiple sources are used
When the assistant answers from a web search, the pages it used are shown as
sources at the end of its reply.
"""

import pytest
from auto_fxui.browser_object import SmartBar, SmartWindowChat
from selenium.webdriver import Firefox

PROMPT = "What do scientists know about how life first began on Earth?"
REPLY = "Life probably began in a primordial soup, and RNA may have come first."


@pytest.fixture()
def test_case():
    return "4255868"


def test_web_sources_shown_after_reply(
    driver: Firefox, smart_window_chat: SmartWindowChat, web_search_sources
):
    """
    C4255868 - Verify that Exa search sources are displayed inline when multiple sources are used
    """
    sources = web_search_sources(PROMPT, REPLY)
    chat = smart_window_chat

    SmartBar(driver).open_full_page_chat()
    chat.send(PROMPT)

    assert chat.get_last_reply() == REPLY
    chat.expect_sources(len(sources))
    shown = chat.get_sources()
    assert [(s["title"], s["url"]) for s in shown] == [
        (s["title"], s["url"]) for s in sources
    ]
    assert chat.sources_follow_last_reply(), "The sources aren't after the reply"
