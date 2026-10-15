import pytest
from selenium.webdriver import Firefox, Keys

from modules.page_object import AboutPrefs

ENGINE_NAME = "Google"
MAX_TAB_STOPS = 60


@pytest.fixture()
def about_prefs_category():
    return "search"


@pytest.fixture()
def test_case():
    return "4105793"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [("browser.settings-redesign.enabled", True)]


def tab_to_engine_toggle(driver: Firefox, about_prefs: AboutPrefs):
    """Press Tab until the engine's toggle has focus."""
    toggle = about_prefs.get_element(
        "search-shortcuts-engine-toggle", labels=[ENGINE_NAME]
    )
    for _ in range(MAX_TAB_STOPS):
        about_prefs.actions.send_keys(Keys.TAB).perform()
        if driver.switch_to.active_element == toggle:
            break
    assert driver.switch_to.active_element == toggle, "Tab never reached the toggle"


def test_engines_toggle_with_keyboard(driver: Firefox, about_prefs: AboutPrefs):
    """
    C4105793 - Engines can be enabled/disabled using only keyboard actions.
    """
    # Step 1: Open about:preferences#search.
    about_prefs.open()
    enabled_engines = about_prefs.get_enabled_search_engines()
    assert ENGINE_NAME in enabled_engines, (
        f"{ENGINE_NAME} not enabled: {enabled_engines}"
    )

    # Step 2: Press Tab until the engine's toggle has focus.
    tab_to_engine_toggle(driver, about_prefs)

    # Step 3: Press Space to switch the engine off.
    about_prefs.actions.send_keys(Keys.SPACE).perform()
    about_prefs.expect(
        lambda _: ENGINE_NAME not in about_prefs.get_enabled_search_engines()
    )

    # Step 4: The engine is gone from the default engine dropdown.
    options = about_prefs.get_default_engine_dropdown_options()
    assert ENGINE_NAME not in options, f"{ENGINE_NAME} still in dropdown: {options}"

    # Press Enter to switch the engine back on.
    tab_to_engine_toggle(driver, about_prefs)
    about_prefs.actions.send_keys(Keys.ENTER).perform()
    about_prefs.expect(
        lambda _: ENGINE_NAME in about_prefs.get_enabled_search_engines()
    )
