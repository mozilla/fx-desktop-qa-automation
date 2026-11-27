"""
C4255969 - Verify that Website sources are displayed inside the Chat Sidebar
Asked from the sidebar beside an article, the reply's sources fit the narrow
sidebar, and the grouped ones show when expanded.
"""

import pytest
from auto_fxui.browser_object import SmartBar, SmartWindowChat
from selenium.webdriver import Firefox

PROMPT = "Compare this page with other articles and summarize a few facts from each."
REPLY = (
    "Each article agrees life began from simple chemistry, with different first steps."
)


@pytest.fixture()
def test_case():
    return "4255969"


def test_web_sources_in_sidebar(
    driver: Firefox, smart_window_chat: SmartWindowChat, web_search_sources, tab_pages
):
    """
    C4255969 - Verify that Website sources are displayed inside the Chat Sidebar
    """
    sources = web_search_sources(PROMPT, REPLY)
    chat = smart_window_chat

    driver.get(tab_pages(["abiogenesis.html"])[0])
    SmartBar(driver).open_smart_bar()
    chat.send(PROMPT)
    chat.expect_sources(len(sources))

    shown = chat.get_sources()
    assert [s["url"] for s in shown] == [s["url"] for s in sources]
    assert all(s["visible"] for s in shown if not s["grouped"])
    grouped = [s for s in shown if s["grouped"]]
    assert grouped, f"The sidebar didn't group any sources: {shown}"

    chat.open_grouped_sources()
    panel = chat.get_grouped_sources()
    assert [s["url"] for s in panel] == [s["url"] for s in grouped]
    assert all(s["visible"] for s in panel), f"A grouped source is hidden: {panel}"
