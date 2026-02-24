import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, TabBar
from modules.page_object import AboutPrefs

TOTAL_TABS = 8
PINNED_TABS = 3
CONTENT_URL = "about:robots"


@pytest.fixture()
def test_case():
    return "2693897"


@pytest.fixture()
def add_to_prefs_list():
    return [("browser.tabs.hoverPreview.enabled", True)]


def _hover_over_tabs_and_verify_preview(
    tabs: TabBar,
    total_tabs: int,
    probe_tab_index: int,
) -> None:
    """Hover each tab and verify hover preview panel appears.

    Validates Title + URL on a single tab (probe_tab_index).
    """
    for i in range(1, total_tabs + 1):
        tab = tabs.get_tab(i)
        assert tab is not None

        tabs.hover(tab)
        tabs.element_visible("tab-preview-panel")

        if i == probe_tab_index:
            tabs.element_visible("tab-preview-title")
            tabs.element_visible("tab-preview-uri")


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

    # Pin the first few tabs while they're guaranteed to be in view.
    for i in range(1, PINNED_TABS + 1):
        tab = tabs.get_tab(i)
        assert tab is not None
        tabs.context_click(tab)
        tab_context_menu.click_and_hide_menu("context-menu-pin-tab")

        if i < PINNED_TABS:
            tabs.new_tab_by_button()

    # Open remaining tabs without forcing tab overflow.
    for _ in range(TOTAL_TABS - PINNED_TABS):
        tabs.new_tab_by_button()

    # Make one tab contentful (offline) so Title+URL are guaranteed.
    probe_tab_index = TOTAL_TABS
    tabs.click_tab_by_index(probe_tab_index)
    with driver.context(driver.CONTEXT_CONTENT):
        driver.get(CONTENT_URL)

    # Hover previews may behave differently for the active tab; switch away.
    tabs.click_tab_by_index(1)

    # Hover over tabs to check if preview exists
    _hover_over_tabs_and_verify_preview(tabs, TOTAL_TABS, probe_tab_index)

    # Uncheck image preview
    about_prefs.open()
    about_prefs.find_in_settings("show an image preview")
    checkbox = about_prefs.get_element("tab-hover-preview-checkbox")
    if isinstance(checkbox, list):
        checkbox = checkbox[0]
    checkbox.click()

    # Hover over tabs again
    _hover_over_tabs_and_verify_preview(tabs, TOTAL_TABS, probe_tab_index)
