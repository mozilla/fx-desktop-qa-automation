import pytest

from modules.browser_object import Navigation
from modules.browser_object_panel_ui import PanelUi
from modules.page_object_customize_firefox import CustomizeFirefox
from modules.page_object_prefs import AboutPrefs

RANDOM_TEXT = "cluj"


@pytest.fixture()
def test_case():
    return "3028773"


def test_search_suggestions_pref_affects_urlbar_and_searchbar(driver):
    nav = Navigation(driver)
    prefs = AboutPrefs(driver, category="search")
    panel_ui = PanelUi(driver)
    customize = CustomizeFirefox(driver)

    # Add legacy search bar to toolbar.
    panel_ui.open_panel_menu()
    panel_ui.navigate_to_customize_toolbar()
    customize.add_widget_to_toolbar("search-bar")

    # --- Step 1: Disable the pref
    prefs.open()
    prefs.select_search_suggestions_in_address_bar(False)

    # --- Step 2: Validate NO suggestions when disabled (both in awesome and search bar)
    for search_mode in ["search", "awesome"]:
        has_suggestions = nav.search_and_check_if_suggestions_are_present(
            RANDOM_TEXT, search_mode
        )
        assert not has_suggestions, (
            "Suggestions should be disabled for the Address Bar."
        )

    # --- Step 3: Re-enable to restore the original state
    prefs.open()
    prefs.select_search_suggestions_in_address_bar(True)

    # --- Step 4: Validate that suggestions appear when enabled
    for search_mode in ["search", "awesome"]:
        has_suggestions = nav.search_and_check_if_suggestions_are_present(
            RANDOM_TEXT, search_mode, 3
        )
        assert has_suggestions, (
            f"{search_mode} Suggestions should be visible for the Address Bar when enabled."
        )
