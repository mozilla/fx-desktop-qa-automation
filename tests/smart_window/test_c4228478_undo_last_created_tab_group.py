"""
C4228478 - Verify that the user can Undo the Last created Tab group
Ungroup Tabs in the Just created section removes the group made from the panel.
"""

import pytest
from auto_fxui.browser_object import OrganizeTabs, SmartWindow, TabBar
from auto_fxui.mock_server import MockServer

RECIPES = ["lasagna.html", "cookie_recipe.html", "recipe_links.html"]
TRAVEL = ["flights.html", "hotels.html"]


@pytest.fixture()
def test_case():
    return "4228478"


@pytest.fixture()
def add_to_prefs_list():
    return [("browser.smartwindow.autoTabGrouping.preloadModels", False)]


def test_undo_last_created_tab_group(
    active_smart_window: SmartWindow, mock_server: MockServer, tab_pages, driver
):
    """
    C4228478 - Verify that the user can Undo the Last created Tab group
    """
    active_smart_window.stub_fxa_token()
    tabs = TabBar(driver)
    recipe_urls, travel_urls = tab_pages(RECIPES), tab_pages(TRAVEL)
    tabs.open_urls_in_tabs(recipe_urls + travel_urls, open_first_in_current_tab=True)

    organize_tabs = OrganizeTabs(driver)
    organize_tabs.stub_clusters([recipe_urls, travel_urls])
    organize_tabs.open_panel()
    organize_tabs.expect_suggestions(2)
    organize_tabs.create_suggested_group(0)
    tabs.expect_tabs_grouped(recipe_urls)
    organize_tabs.expect_recent_groups(1)

    organize_tabs.click_ungroup()
    tabs.wait.until(
        lambda _: not tabs.get_tab_groups(), message="The group was not removed"
    )
    assert set(tabs.get_tab_urls()) == set(recipe_urls + travel_urls)
