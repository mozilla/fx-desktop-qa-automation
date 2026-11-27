"""
C4228476 - Verify that the user can create an individual group from the Suggested Groups section
Hovering a suggested group lists its tabs, and clicking it groups exactly those tabs.
"""

import pytest
from auto_fxui.browser_object import OrganizeTabs, SmartWindow, TabBar
from auto_fxui.mock_server import MockServer

RECIPES = ["lasagna.html", "cookie_recipe.html", "recipe_links.html"]
TRAVEL = ["flights.html", "hotels.html"]
RECIPE_TITLES = {
    "The Very Best Lasagna Recipe",
    "Chewy Chocolate Chip Cookies Recipe",
    "Recipe Links",
}


@pytest.fixture()
def test_case():
    return "4228476"


@pytest.fixture()
def add_to_prefs_list():
    return [("browser.smartwindow.autoTabGrouping.preloadModels", False)]


def test_create_group_from_suggested_groups(
    active_smart_window: SmartWindow, mock_server: MockServer, tab_pages, driver
):
    """
    C4228476 - Verify that the user can create an individual group from the Suggested Groups section
    """
    active_smart_window.stub_fxa_token()
    tabs = TabBar(driver)
    recipe_urls, travel_urls = tab_pages(RECIPES), tab_pages(TRAVEL)
    tabs.open_urls_in_tabs(recipe_urls + travel_urls, open_first_in_current_tab=True)

    organize_tabs = OrganizeTabs(driver)
    organize_tabs.stub_clusters([recipe_urls, travel_urls])
    organize_tabs.open_panel()
    organize_tabs.expect_suggestions(2)

    organize_tabs.hover_suggestion(0)
    assert set(organize_tabs.get_flyout_tab_titles()) == RECIPE_TITLES

    organize_tabs.create_suggested_group(0)
    tabs.expect_tabs_grouped(recipe_urls)
    groups = tabs.get_tab_groups()
    assert [set(g["urls"]) for g in groups] == [set(recipe_urls)]
