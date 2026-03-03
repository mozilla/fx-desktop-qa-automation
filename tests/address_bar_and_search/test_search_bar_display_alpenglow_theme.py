import pytest
from selenium.webdriver import Firefox, Keys

from modules.browser_object_navigation import Navigation
from modules.page_object_prefs import AboutAddons

TEXT = "Firefox"


@pytest.fixture()
def test_case():
    return "3028997"


def test_search_bar_display_alpenglow_theme(driver: Firefox):
    """
    C3028997 - Search bar is correctly displayed on Alpenglow theme
    """

    # Instantiate objects
    nav = Navigation(driver)
    abt_addons = AboutAddons(driver)

    # Have the Proton Alpenglow theme Activated
    abt_addons.open()
    abt_addons.choose_sidebar_option("theme")
    abt_addons.activate_theme(
        nav, "firefox-alpenglow_mozilla_org-heading", "", perform_assert=False
    )

    # Add the Search bar to Toolbar
    nav.add_search_bar_to_toolbar()

    # Open a new tab and hit Ctrl/Cmd + K
    nav.open_and_switch_to_new_window("tab")
    nav.perform_key_combo_chrome(Keys.CONTROL, "k")

    # The search bar is in focus and no visual errors are displayed
    nav.verify_search_bar_is_focused()

    # Write an input
    nav.type_in_search_bar(TEXT)

    # Wait until the search suggestions dropdown is visible
    nav.wait_for_searchbar_suggestions()

    # Hit the Down Arrow key to navigate through suggestions
    for _ in range(2):
        nav.perform_key_combo_chrome(Keys.DOWN)

    # The highlight goes through the suggestions accordingly
    nav.verify_searchbar_suggestion_is_highlighted()

    # # Click the default search engine button to open the engine picker popup
    # nav.click_search_engine_button()
    #
    # # Navigate through the search engine suggestions with Tab
    # nav.perform_key_combo_chrome(Keys.TAB)
    # nav.verify_searchmode_engine_is_focused("Google")
    #
    # nav.perform_key_combo_chrome(Keys.TAB)
    # nav.verify_searchmode_engine_is_focused("Amazon.com")
