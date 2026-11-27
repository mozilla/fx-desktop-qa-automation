"""
C4255967 - Verify that the Website sources are visibile with High contrast
With forced (high contrast) colors on, the sources and the grouped sources
are shown, and their labels stand out from what's behind them.
"""

import pytest
from auto_fxui.browser_object import SmartBar, SmartWindowChat
from selenium.webdriver import Firefox

PROMPT = "Compare reviews of origin-of-life theories from multiple websites."
REPLY = "Most reviews favour the RNA world hypothesis."


@pytest.fixture()
def test_case():
    return "4255967"


@pytest.fixture()
def add_to_prefs_list():
    # Always override page colors, which turns on forced-colors, as High Contrast does.
    return [("browser.display.document_color_use", 2)]


def test_web_sources_high_contrast(
    driver: Firefox, smart_window_chat: SmartWindowChat, web_search_sources
):
    """
    C4255967 - Verify that the Website sources are visibile with High contrast
    """
    sources = web_search_sources(PROMPT, REPLY)
    chat = smart_window_chat

    # The sidebar, so that some of the three sources are grouped.
    SmartBar(driver).open_smart_bar()
    chat.send(PROMPT)
    chat.expect_sources(len(sources))
    assert chat.is_forced_colors_active(), "High contrast (forced colors) is off"

    shown = [s for s in chat.get_sources() if not s["grouped"]]
    assert shown and all(s["visible"] for s in shown)
    colors = chat.get_source_colors()
    assert colors and all(c["color"] != c["background"] for c in colors), colors

    chat.open_grouped_sources()
    assert all(s["visible"] for s in chat.get_grouped_sources())
    colors = chat.get_source_colors(grouped=True)
    assert colors and all(c["color"] != c["background"] for c in colors), colors
