import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from modules.browser_object_navigation import Navigation
from modules.browser_object_tabbar import TabBar
from modules.page_object_prefs import AboutPrefs

TEST_TEXT_1 = "firefox handoff test"
TEST_TEXT_2 = "new tab handoff"
TEST_TEXT_3 = "handoff search field test"


@pytest.fixture()
def test_case():
    return "3028951"


def test_handoff_to_address_bar(driver: Firefox):
    """
    C3028951 - Verify that Hand-off to the address bar works as designed.

    Precondition: Ensure default search engine is set to Google.
    Step 1: Type text in the awesome bar and verify it appears.
    Step 2: Open a new tab using the "+" button, type text, and verify it appears.
    Step 3: Open another new tab, type on the search handoff control,
            and verify the text is handed off to the awesome bar.
    """
    nav = Navigation(driver)
    tabs = TabBar(driver)
    prefs = AboutPrefs(driver, category="search")

    # Precondition: set default search engine to Google
    prefs.open()
    prefs.search_engine_dropdown().select_option("Google")

    # Step 1: Type into the awesome bar and confirm the text
    nav.clear_awesome_bar()
    nav.type_in_awesome_bar(TEST_TEXT_1)
    current_text = nav.get_awesome_bar_text()
    assert TEST_TEXT_1 in current_text, f"Expected '{TEST_TEXT_1}' in the awesome bar, found '{current_text}'."

    # --- Step 2: Open a new tab via the tab bar "+" button and type text
    tabs.new_tab_by_button()
    tabs.switch_to_new_tab()
    nav.type_in_awesome_bar(TEST_TEXT_2)
    current_text_new_tab = nav.get_awesome_bar_text()
    assert TEST_TEXT_2 in current_text_new_tab, (
        f"Expected '{TEST_TEXT_2}' in the awesome bar on the new tab, found '{current_text_new_tab}'."
    )

    # Step 3: Open another tab, type on in the "search on web" (button), verify handoff occurred
    tabs.new_tab_by_button()
    tabs.switch_to_new_tab()

    handoff_btn = driver.find_element(By.CSS_SELECTOR, ".search-handoff-button")
    handoff_btn.click()                 # focus the handoff control
    handoff_btn.send_keys(TEST_TEXT_3)  # typing here should hand off to the urlbar

    current_text_handoff = nav.get_awesome_bar_text()
    assert TEST_TEXT_3 in current_text_handoff, (
        f"Expected '{TEST_TEXT_3}' to be handed off to the awesome bar, found '{current_text_handoff}'."
    )
