import pytest
from selenium.webdriver import Firefox, Keys

from modules.browser_object_navigation import Navigation
from modules.browser_object_panel_ui import PanelUi
from modules.page_object_customize_firefox import CustomizeFirefox
from modules.page_object_prefs import AboutAddons


TEXT = "Firefox"


@pytest.fixture()
def test_case():
    return "3028997"


def test_searchbar_display_alpenglow_theme(driver: Firefox):
    """
    C3028997 - Search bar is correctly displayed on Alpenglow theme
    """

    # Instantiate objects
    nav = Navigation(driver)
    abt_addons = AboutAddons(driver)
    panel_ui = PanelUi(driver)
    customize = CustomizeFirefox(driver)

    # Have the Proton Alpenglow theme Activated
    abt_addons.open()
    abt_addons.choose_sidebar_option("theme")
    abt_addons.activate_theme(
        nav, "firefox-alpenglow_mozilla_org-heading", "", perform_assert=False
    )

    # Add the Search bar to Toolbar
    panel_ui.open_panel_menu()
    panel_ui.navigate_to_customize_toolbar()
    customize.add_widget_to_toolbar("search-bar")

    # Open a new tab and hit Ctrl/Cmd + K
    nav.open_and_switch_to_new_window("tab")
    nav.perform_key_combo_chrome(Keys.COMMAND, "k")

    # Write an input
    nav.type_in_search_bar(TEXT)

    # Wait until the search suggestions dropdown is visible
    nav.wait_for_searchbar_suggestions()

    # Hit Tab a few times
    for _ in range(2):
        nav.perform_key_combo_chrome(Keys.TAB)

    # The highlight goes through the one-off buttons accordingly
    nav.verify_searchbar_engine_is_focused("Bing")

    # Hit the down Arrow key a few times
    for _ in range(2):
        nav.perform_key_combo_chrome(Keys.DOWN)

    # The highlight goes through the one-off buttons accordingly
    nav.verify_searchbar_engine_is_focused("eBay")
