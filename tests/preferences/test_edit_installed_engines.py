import pytest
from selenium.webdriver import Firefox, Keys

from modules.browser_object import Navigation, TabBar
from modules.page_object import AboutPrefs

ENGINE_ID = "wikipedia"
ENGINE_NAME = "Wikipedia (en)"
NEW_KEYWORD = "starfoxkw"


@pytest.fixture()
def about_prefs_category():
    return "search"


@pytest.fixture()
def test_case():
    return "4105792"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [("browser.settings-redesign.enabled", True)]


def test_edit_installed_engines(
    driver: Firefox, about_prefs: AboutPrefs, nav: Navigation, tabs: TabBar
):
    """
    C4105792 - Editing installed engines works.
    """
    # Step 1: Open about:preferences#search and find the engine.
    about_prefs.open()
    about_prefs.element_visible("search-shortcuts-engine-row", labels=[ENGINE_NAME])

    # Steps 2 and 3: Add a keyword from the engine's Edit dialog.
    about_prefs.edit_search_engine_keyword(ENGINE_ID, NEW_KEYWORD)

    # The engine row lists the new keyword.
    about_prefs.element_attribute_contains(
        "search-shortcuts-engine-row", "description", NEW_KEYWORD, labels=[ENGINE_NAME]
    )

    # Step 4: The keyword opens search mode for the engine.
    tabs.open_and_switch_to_new_tab()
    nav.type_in_awesome_bar(NEW_KEYWORD)
    # Give Firefox time to process the keyword before pressing space.
    nav.perform_key_combo_chrome(Keys.SPACE)
    nav.verify_search_mode_is_visible(ENGINE_NAME)
