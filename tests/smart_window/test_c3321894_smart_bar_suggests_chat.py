"""
C3321894 - Verify that the Smart bar suggestions recognizes the users intent to chat
Typing a question into the Smart Bar offers a chat suggestion for it, alongside
the default search engine's suggestions for the same text.
"""

import pytest
from auto_fxui.browser_object import SmartBar, SmartWindow
from auto_fxui.browser_object_smart_bar import (
    PROVIDER_AI_CHAT,
    PROVIDER_SEARCH_SUGGESTIONS,
)
from selenium.webdriver import Firefox

QUERY = "what is a dinos"


@pytest.fixture()
def test_case():
    return "3321894"


def test_smart_bar_suggests_chat(driver: Firefox, active_smart_window: SmartWindow):
    """
    C3321894 - Verify that the Smart bar suggestions recognizes the users intent to chat
    """
    # Instantiate objects
    smart_bar = SmartBar(driver)

    smart_bar.open_full_page_chat()
    smart_bar.set_smart_bar_text(QUERY)
    smart_bar.expect_results_from(PROVIDER_AI_CHAT, PROVIDER_SEARCH_SUGGESTIONS)
    results = smart_bar.get_results()

    chat = [r["text"] for r in results if r["provider"] == PROVIDER_AI_CHAT]
    assert chat == [QUERY], f"Expected one chat suggestion for {QUERY!r}: {results}"

    # Search suggestions come live from the engine, so check they relate to the
    # query rather than matching exact text.
    assert smart_bar.get_default_search_engine() == "Google"
    suggestions = [
        r["text"] for r in results if r["provider"] == PROVIDER_SEARCH_SUGGESTIONS
    ]
    unrelated = [s for s in suggestions if "dinos" not in s.lower()]
    assert not unrelated, f"Suggestions unrelated to {QUERY!r}: {unrelated}"
