import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, Navigation, TabBar

GROUP_NAME = ["group1", "group2", "group3"]
URLS = ["https://example.com", "https://example.org"]


@pytest.fixture()
def test_case():
    return "2793050"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.tabs.groups.enabled", True),
        ("browser.tabs.groups.dragOverThresholdPercent", 20),
    ]


@pytest.mark.parametrize(
    "enable_vertical_tabs, group_name",
    [
        (False, GROUP_NAME[0]),
        (True, GROUP_NAME[1]),
    ],
    ids=["default_tabs", "vertical_tabs"],
)
def test_save_and_close_tab_group(
    driver: Firefox, enable_vertical_tabs: bool, group_name: str
):
    """
    C2793050 - Verify that the user can Save and Close a tab group on two scenarios, with horizontal and vertical
    tabs enabled.
    """
    tabs = TabBar(driver)
    context_menu = ContextMenu(driver)
    nav = Navigation(driver)

    # Enable vertical tabs when required for this parametrized case
    if enable_vertical_tabs:
        nav.context_click("toolbar-blank-space")
        context_menu.click_on("context-menu-vertical-tabs")

    # Open URLs in new tabs — keeps the initial tab alive outside the group
    # so Firefox doesn't close when the group is saved and closed.
    # Save and Close also requires tabs with bookmarkable URLs (not about:newtab).
    tabs.open_urls_in_tabs(URLS, open_first_in_current_tab=False)

    # Create a tab group from the URL-loaded tabs (tabs 2 and 3)
    tabs.create_websites_tab_group(
        context_menu=context_menu,
        group_name=group_name,
        first_tab_index=2,
        additional_tab_indexes=[3],
    )

    # Right-click the Tab Group label and select Save and Close Group
    tabs.save_and_close_tab_group()

    # Verify the group label is removed
    tabs.element_not_visible("tabgroup-label")
