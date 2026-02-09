import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, TabBar

URLS = [
    "about:about",
    "about:mozilla",
    "about:license",
]

MOVE_TO_START = "context-menu-move-tab-to-start"
MOVE_TO_END = "context-menu-move-tab-to-end"
MOVE_TO_NEW_WINDOW = "context-menu-move-to-new-window"
MOVE_TAB_MENU = "context-menu-move-tab"

# Close Multiple Tabs submenu locators (to be updated)
CLOSE_MULTIPLE_TABS_MENU = "context-menu-close-multiple-tabs"
CLOSE_TABS_TO_RIGHT = "context-menu-close-multiple-tabs-to-right"
CLOSE_OTHER_TABS = "context-menu-close-multiple-tabs-other-tabs"
CLOSE_TABS_TO_LEFT = "context-menu-close-multiple-tabs-to-left"
RELOAD_TAB = "context-menu_reload-tab"


@pytest.fixture()
def test_case():
    return "246991"


@pytest.mark.parametrize(
    "move_option", [MOVE_TO_START, MOVE_TO_END, MOVE_TO_NEW_WINDOW]
)
def test_move_single_tab_via_context_menu(driver: Firefox, move_option: str):
    """
    C246991 - Test tab repositioning via Move Tab context menu options.
    """
    # Instantiate objects
    tabs = TabBar(driver)
    context_menu = ContextMenu(driver)

    # Open all URLs in tabs and collect titles
    tabs.open_urls_in_tabs(URLS, open_first_in_current_tab=True)
    titles = []
    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        titles.append(driver.title)

    # Select middle tab (tab index 2, since get_tab is 1-based)
    if move_option == MOVE_TO_END:
        driver.switch_to.window(driver.window_handles[0])
        expected_title = titles[0]
    else:
        expected_title = titles[-1]

    # Right-click on the selected tab and click the move option
    tabs.context_click("selected-tab")
    context_menu.click_context_item(MOVE_TAB_MENU)

    # Verify Move Tab submenu has all expected options
    context_menu.element_visible(MOVE_TO_START)
    context_menu.element_visible(MOVE_TO_END)
    context_menu.element_visible(MOVE_TO_NEW_WINDOW)

    # Click the specific option
    context_menu.element_clickable(move_option)
    context_menu.click_on(move_option)
    tabs.hide_popup("tabContextMenu")

    # Verify the selected tab is moved to expected position with correct title
    if move_option == MOVE_TO_START:
        driver.switch_to.window(driver.window_handles[0])
    else:
        driver.switch_to.window(driver.window_handles[-1])

    assert expected_title in driver.title


@pytest.mark.parametrize(
    "close_option", [CLOSE_TABS_TO_RIGHT, CLOSE_OTHER_TABS, RELOAD_TAB]
)
def test_close_tabs_via_context_menu(driver: Firefox, close_option: str):
    """
    C246991 - Steps 6-9: Test Close Multiple Tabs submenu options and Reload Tab.
    """
    # Instantiate objects
    tabs = TabBar(driver)
    context_menu = ContextMenu(driver)

    # Open all URLs in tabs
    tabs.open_urls_in_tabs(URLS, open_first_in_current_tab=True)
    initial_tab_count = len(driver.window_handles)

    # Select middle tab (tab index 2, since get_tab is 1-based)
    driver.switch_to.window(driver.window_handles[1])
    selected_tab_title = driver.title
    middle_tab = tabs.get_tab(2)

    # Right-click on the selected tab and click the close option
    tabs.context_click(middle_tab)
    if close_option == RELOAD_TAB:
        # Reload Tab is a direct option in the context menu
        context_menu.click_and_hide_menu(close_option)
    else:
        # Verify Close Multiple Tabs submenu options exist
        context_menu.click_context_item(CLOSE_MULTIPLE_TABS_MENU)
        context_menu.element_visible(CLOSE_TABS_TO_RIGHT)
        context_menu.element_visible(CLOSE_OTHER_TABS)
        context_menu.element_visible(CLOSE_TABS_TO_LEFT)

        # Click the specific option
        context_menu.click_and_hide_menu(close_option)
    tabs.hide_popup("tabContextMenu")

    # Verify expected tabs are closed and selected tab is in expected position with correct title
    if close_option == CLOSE_TABS_TO_RIGHT:
        # All tabs to the right of selected tab get closed
        tabs.wait_for_num_tabs(2)
        driver.switch_to.window(driver.window_handles[-1])
        assert driver.title == selected_tab_title
    elif close_option == CLOSE_OTHER_TABS:
        # All tabs except selected tab get closed
        tabs.wait_for_num_tabs(1)
        assert driver.title == selected_tab_title
    elif close_option == RELOAD_TAB:
        # Tab gets reloaded
        assert driver.title == selected_tab_title
