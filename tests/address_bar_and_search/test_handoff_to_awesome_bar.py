import time

import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.browser_object_tabbar import TabBar
from modules.page_object_prefs import AboutPrefs

TEST_TEXT_1 = "firefox handoff test"
TEST_TEXT_2 = "new tab handoff"
TEST_TEXT_3 = "handoff search field test"


@pytest.fixture()
def test_case():
    return "3028951"


def test_handoff_to_awesome_bar(driver: Firefox):
    """
    C3028951 - Verify that Hand-off to the address bar works as designed.

    Precondition: Ensure default search engine is set to Google.
    Step 1: Type text in the awesome bar and verify it appears.
    Step 2: Open a new tab using the '+' button, type text, and verify it appears.
    Step 3: Open another new tab, click the search handoff control and type via OS
            keyboard (pynput). Verify the text is handed off to the awesome bar.
    """
    nav = Navigation(driver)
    tabs = TabBar(driver)
    prefs = AboutPrefs(driver, category="search")

    # Precondition: set default search engine to Google
    prefs.open()
    prefs.search_engine_dropdown().select_option("Google")

    # Type into the awesome bar and confirm the text
    nav.clear_awesome_bar()
    nav.type_in_awesome_bar(TEST_TEXT_1)
    assert TEST_TEXT_1 in nav.get_awesome_bar_text(), (
        f"Expected '{TEST_TEXT_1}' in the awesome bar."
    )

    # Open a new tab via the '+' button and type text
    tabs.new_tab_by_button()
    tabs.switch_to_new_tab()
    nav.type_in_awesome_bar(TEST_TEXT_2)
    assert TEST_TEXT_2 in nav.get_awesome_bar_text(), (
        f"Expected '{TEST_TEXT_2}' in the awesome bar on the new tab."
    )

    # Open another tab; click the search handoff control, then type via pynput
    tabs.new_tab_by_button()
    tabs.switch_to_new_tab()

    nav.get_element("search-handoff-button").click()
    time.sleep(0.5)  # Let focus move from input field → awesome bar

    # Direct pynput typing
    from pynput.keyboard import Controller
    kb = Controller()
    kb.type(TEST_TEXT_3)

    # Verify handoff ended up in the awesome bar
    assert TEST_TEXT_3 in nav.get_awesome_bar_text(), (
        f"Expected '{TEST_TEXT_3}' to be handed off to the awesome bar."
    )
