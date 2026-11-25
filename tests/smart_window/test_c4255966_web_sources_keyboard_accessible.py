"""
C4255966 - Verify that the Website sources are keyboard Accessible
A source can be reached with the keyboard from the Smart Bar and opened in a
new tab with Enter.
"""

import pytest
from auto_fxui.browser_object import SmartBar, SmartWindowChat, TabBar
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

PROMPT = "Compare reviews of the origin-of-life theories from multiple websites."
REPLY = "Reviewers favour the RNA world, though the primordial soup still has support."


@pytest.fixture()
def test_case():
    return "4255966"


def test_web_sources_keyboard_accessible(
    driver: Firefox, smart_window_chat: SmartWindowChat, web_search_sources
):
    """
    C4255966 - Verify that the Website sources are keyboard Accessible
    """
    sources = web_search_sources(PROMPT, REPLY)
    chat = smart_window_chat
    tabs = TabBar(driver)

    SmartBar(driver).open_full_page_chat()
    chat.send(PROMPT)
    chat.expect_sources(len(sources))

    source = chat.tab_to_source()
    assert source in [s["url"] for s in sources]
    chat.perform_key_combo_chrome(Keys.ENTER)
    tabs.expect(lambda _: source in tabs.get_tab_urls())
