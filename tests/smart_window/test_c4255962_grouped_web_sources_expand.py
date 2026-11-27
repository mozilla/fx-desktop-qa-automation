"""
C4255962 - Verify that when multiple Exa web search sources are available they are grouped together and can be expanded
Sources that don't fit beside the first are grouped behind a "+n more"
button, which opens a panel listing them with their icons.
"""

import pytest
from auto_fxui.browser_object import SmartBar, SmartWindowChat
from selenium.webdriver import Firefox

PROMPT = (
    "Tell me everything in detail about abiogenesis, who started the field, "
    "and what breakthroughs we had since then."
)
REPLY = "Oparin and Haldane started the field; Miller and Urey ran the first test."


@pytest.fixture()
def test_case():
    return "4255962"


def test_grouped_web_sources_expand(
    driver: Firefox, smart_window_chat: SmartWindowChat, web_search_sources
):
    """
    C4255962 - Verify that when multiple Exa web search sources are available they are grouped together and can be expanded
    """
    sources = web_search_sources(PROMPT, REPLY)
    chat = smart_window_chat

    # The full-page chat fits all three sources in a row; the sidebar groups them.
    SmartBar(driver).open_smart_bar()
    chat.send(PROMPT)
    chat.expect_sources(len(sources))

    all_sources = chat.get_sources()
    grouped = [s for s in all_sources if s["grouped"]]
    assert grouped, f"No sources were grouped: {all_sources}"
    chat.expect(lambda _: chat.get_grouped_sources_label() == f"+{len(grouped)} more")

    chat.open_grouped_sources()
    panel = chat.get_grouped_sources()
    assert [(s["title"], s["url"]) for s in panel] == [
        (s["title"], s["url"]) for s in grouped
    ]
    assert all(s["icon"] for s in panel), f"A grouped source has no icon: {panel}"
