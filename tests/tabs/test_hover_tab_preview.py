import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, TabBar
from modules.page_object import AboutPrefs

TOTAL_TABS = 8
PINNED_TABS = 3


@pytest.fixture()
def test_case():
    return "2693897"


@pytest.fixture()
def add_to_prefs_list():
    return [("browser.tabs.hoverPreview.enabled", True)]


def _hover_over_tabs_and_verify_preview(
    tabs: TabBar,
    total_tabs: int,
    check_thumbnail: bool,
) -> None:
    """Hover each tab and verify hover preview panel appears.

    Validates Title + URL on every tab.
    If check_thumbnail is True, validates thumbnail is visible.
    If check_thumbnail is False, validates thumbnail is not visible.
    """
    tabs.click_tab_by_index(1)

    for i in range(2, total_tabs + 1):
        tab = tabs.get_tab(i)
        assert tab is not None

        tabs.hover(tab)
        tabs.element_visible("tab-preview-panel")
        tabs.element_visible("tab-preview-title")
        tabs.element_visible("tab-preview-uri")

        if check_thumbnail:
            tabs.element_visible("tab-preview-thumbnail-container")
        else:
            tabs.element_not_visible("tab-preview-thumbnail-container")

    # Hover tab 1 while not active tab
    tabs.click_tab_by_index(2)
    tab = tabs.get_tab(1)
    assert tab is not None

    tabs.hover(tab)
    tabs.element_visible("tab-preview-panel")
    tabs.element_visible("tab-preview-title")
    tabs.element_visible("tab-preview-uri")

    if check_thumbnail:
        tabs.element_visible("tab-preview-thumbnail-container")
    else:
        tabs.element_not_visible("tab-preview-thumbnail-container")

    # Return to tab 1 to uncheck pref
    tabs.click_tab_by_index(1)


def test_hover_tab_preview(driver: Firefox):
    """C2693897: Verify tab hover preview works with many tabs.

    - Open many tabs (including pinned tabs).
    - Hover each tab and verify hover preview panel shows Name + URL.
    - Disable "Show an image preview when you hover on a tab".
    - Hover each tab again and verify preview still shows Name + URL (no thumbnail).
    """
    # Instantiate objects
    tabs = TabBar(driver)
    tab_context_menu = ContextMenu(driver)
    about_prefs = AboutPrefs(driver, category="general")

    # Pin the first few tabs
    for i in range(1, PINNED_TABS + 1):
        tab = tabs.get_tab(i)
        assert tab is not None
        tabs.context_click(tab)
        tab_context_menu.click_and_hide_menu("context-menu-pin-tab")

        if i < PINNED_TABS:
            tabs.new_tab_by_button()

    # Open remaining tabs without entering tab overflow
    for _ in range(TOTAL_TABS - PINNED_TABS):
        tabs.new_tab_by_button()

    # Hover over tabs to check if preview exists
    _hover_over_tabs_and_verify_preview(tabs, TOTAL_TABS, check_thumbnail=True)

    # Uncheck image preview
    about_prefs.open()
    about_prefs.find_in_settings("show an image preview")
    checkbox = about_prefs.get_element("tab-hover-preview-checkbox")
    if isinstance(checkbox, list):
        checkbox = checkbox[0]
    checkbox.click()

    # Hover over tabs again without image preview
    _hover_over_tabs_and_verify_preview(tabs, TOTAL_TABS, check_thumbnail=False)
