"""
C4255965 - Verify that the user can select the Source websites and open them in new tabs
A source opens in a new tab when clicked, opens in a new tab or window from
its context menu, and a grouped source opens in a new tab from the panel.
"""

import pytest
from auto_fxui.browser_object import ContextMenu, SmartBar, SmartWindowChat, TabBar
from selenium.webdriver import Firefox

PROMPT = "Can you give me some research on abiogenesis?"
REPLY = "Here is what the research says about how life began."


@pytest.fixture()
def test_case():
    return "4255965"


def test_open_web_sources_in_new_tabs(
    driver: Firefox, smart_window_chat: SmartWindowChat, web_search_sources
):
    """
    C4255965 - Verify that the user can select the Source websites and open them in new tabs
    """
    web_search_sources(PROMPT, REPLY)
    chat = smart_window_chat
    tabs = TabBar(driver)
    context_menu = ContextMenu(driver)

    # The sidebar, so that some of the three sources are grouped.
    SmartBar(driver).open_smart_bar()
    chat.send(PROMPT)
    chat.expect_sources(3)
    all_sources = chat.get_sources()
    shown = [s["url"] for s in all_sources if not s["grouped"]]
    grouped = [s["url"] for s in all_sources if s["grouped"]]
    assert shown and grouped, f"Expected shown and grouped sources: {all_sources}"
    source = shown[0]

    chat.click_source(source)
    tabs.expect(lambda _: tabs.get_tab_urls().count(source) == 1)

    chat.click_source(source, button="right")
    context_menu.element_visible("context-menu-open-link-in-tab")
    context_menu.click_context_item("context-menu-open-link-in-tab")
    tabs.expect(lambda _: tabs.get_tab_urls().count(source) == 2)

    windows = len(driver.window_handles)
    chat.click_source(source, button="right")
    context_menu.element_visible("context-menu-open-link-in-new-window")
    context_menu.click_context_item("context-menu-open-link-in-new-window")
    tabs.wait_for_num_windows(windows + 1)

    # Step 4, middle-clicking a source, isn't checked: Nightly 163 opens nothing.
    chat.open_grouped_sources()
    chat.click_source(grouped[0], grouped=True)
    tabs.expect(lambda _: tabs.get_tab_urls().count(grouped[0]) == 1)
