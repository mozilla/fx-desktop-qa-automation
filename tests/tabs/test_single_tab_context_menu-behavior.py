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


@pytest.fixture()
def test_case():
    return "246991"


@pytest.mark.parametrize(
    "move_option", [MOVE_TO_START, MOVE_TO_END, MOVE_TO_NEW_WINDOW]
)
def test_move_single_tab_via_context_menu(driver: Firefox, move_option: str):
    """C246991 - Test tab repositioning via Move Tab context menu options."""
    # Instantiate objects
    tabs = TabBar(driver)
    context_menu = ContextMenu(driver)

    # Open all URLs in tabs and collect titles
    tabs.open_urls_in_tabs(URLS, open_first_in_current_tab=True)
    titles = []
    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        titles.append(driver.title)

    if move_option == MOVE_TO_END:
        driver.switch_to.window(driver.window_handles[0])
        expected_title = titles[0]
    else:
        expected_title = titles[-1]

    tabs.context_click("selected-tab")
    context_menu.hover(MOVE_TAB_MENU)
    context_menu.element_clickable(move_option)
    context_menu.click_on(move_option)
    tabs.hide_popup("tabContextMenu")

    if move_option == MOVE_TO_START:
        driver.switch_to.window(driver.window_handles[0])
    else:
        driver.switch_to.window(driver.window_handles[-1])

    assert expected_title in driver.title
