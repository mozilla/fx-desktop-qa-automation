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

    # Open a new tab hit Ctrl/Cmd + K and verify the search bar is in focus
    nav.open_and_switch_to_new_window("tab")
    nav.perform_key_combo_chrome(Keys.CONTROL, "k")
    nav.verify_search_bar_is_focused()

    # Write an input and wait for the search suggestions dropdown to be visible
    nav.type_in_search_bar(TEXT)
    nav.wait_for_searchbar_suggestions()

    # Tab cycles suggestions
    for _ in range(5):
        nav.perform_key_combo_chrome(Keys.TAB)
        nav.verify_searchbar_suggestion_is_highlighted()

    # Down arrow cycles suggestions
    for _ in range(5):
        nav.perform_key_combo_chrome(Keys.DOWN)
        nav.verify_searchbar_suggestion_is_highlighted()
