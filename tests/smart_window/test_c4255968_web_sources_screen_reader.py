"""
C4255968 - Verify that the Websites sources are read out loud by screen readers
Assistive technology gets each source as a link named after its page, both
the one reached with Tab and the grouped ones.
"""

import pytest
from auto_fxui.browser_object import SmartBar, SmartWindowChat
from selenium.webdriver import Firefox

PROMPT = "Compare reviews of the main abiogenesis theories from multiple websites."
REPLY = "The reviews split between the primordial soup and the RNA world."


@pytest.fixture()
def test_case():
    return "4255968"


def test_web_sources_screen_reader(
    driver: Firefox, smart_window_chat: SmartWindowChat, web_search_sources
):
    """
    C4255968 - Verify that the Websites sources are read out loud by screen readers
    """
    sources = web_search_sources(PROMPT, REPLY)
    titles = {s["url"]: s["title"] for s in sources}
    chat = smart_window_chat

    # The sidebar, so that some of the three sources are grouped.
    SmartBar(driver).open_smart_bar()
    chat.send(PROMPT)
    chat.expect_sources(len(sources))

    focused = chat.tab_to_source()
    all_sources = chat.get_sources()
    shown = [s for s in all_sources if not s["grouped"]]
    assert focused in [s["url"] for s in shown]
    assert chat.get_source_accessibles() == [
        {"role": "link", "name": s["title"]} for s in shown
    ]

    grouped = [s for s in all_sources if s["grouped"]]
    more = chat.get_grouped_sources_button_accessible()
    assert more == {"role": "pushbutton", "name": f"+{len(grouped)} more"}

    chat.open_grouped_sources()
    names = [a["name"] for a in chat.get_source_accessibles(grouped=True)]
    assert names == [titles[s["url"]] for s in grouped]
