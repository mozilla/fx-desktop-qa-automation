from typing import Literal

import pytest

from modules.browser_object import Navigation
from modules.browser_object_panel_ui import PanelUi
from modules.browser_object_tabbar import TabBar
from modules.page_object_prefs import AboutPrefs


@pytest.fixture()
def test_case():
    return "3028770"


TERM = "mozilla"
ENGINE_NAME = "DuckDuckGo"
EXPECT_VISIBLE: Literal["visible"] = "visible"
EXPECT_NOT_VISIBLE: Literal["not_visible"] = "not_visible"


def test_searchbar_engine_remove_restore_affects_both_windows(driver):
    """
    C3028770 - Verify that removing and restoring search engines reflects in searchbar engine suggestion,
    both regular and private windows.
    """
    # Initialize objects
    nav = Navigation(driver)
    panel_ui = PanelUi(driver)
    tabs = TabBar(driver)
    prefs = AboutPrefs(driver, category="search")

    # Add search bar to toolbar
    nav.add_search_bar_to_toolbar()

    # Open search settings from searchbar via magnifying glass button, while making sure the targeted engine is present
    tabs.new_tab_by_button()
    tabs.switch_to_new_tab()
    nav.click_on("searchbar-magnifying-glass-button")
    nav.element_visible("searchbar-search-engine", labels=[ENGINE_NAME])
    nav.click_on_change_search_settings_button()

    # Remove the targeted engine
    prefs.select_search_engine_from_tree(ENGINE_NAME)
    prefs.click_on("remove-search-engine button")

    # Verify the targeted engine is removed in regular window
    nav.verify_engine_visibility_in_searchbar_suggestion(
        TERM, ENGINE_NAME, EXPECT_NOT_VISIBLE
    )

    # Verify the targeted engine is removed in private window
    panel_ui.open_and_switch_to_new_window("private")
    nav.verify_engine_visibility_in_searchbar_suggestion(
        TERM, ENGINE_NAME, EXPECT_NOT_VISIBLE
    )

    # Restore the targeted engine search engine
    panel_ui.open_and_switch_to_new_window("window")
    prefs.open()
    prefs.click_on("restore-default-search-engine button")

    # Verify the targeted engine is visible in regular window
    nav.verify_engine_visibility_in_searchbar_suggestion(
        TERM, ENGINE_NAME, EXPECT_VISIBLE
    )

    # Verify the targeted engine is visible in private window
    panel_ui.open_and_switch_to_new_window("private")
    nav.verify_engine_visibility_in_searchbar_suggestion(
        TERM, ENGINE_NAME, EXPECT_VISIBLE
    )
