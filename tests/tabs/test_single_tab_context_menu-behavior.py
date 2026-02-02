import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, TabBar
from modules.page_object_generics import GenericPage

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
    return "C1234567"


@pytest.mark.parametrize(
    "move_option", [MOVE_TO_START, MOVE_TO_END, MOVE_TO_NEW_WINDOW]
)
def test_move_single_tab(driver: Firefox, move_option: str):
    """Test tab repositioning via Move Tab context menu options."""
    tabs = TabBar(driver)
    context_menu = ContextMenu(driver)

    GenericPage(driver, url=URLS[0]).open()
    first_title = driver.title

    tabs.new_tab_by_button()
    driver.switch_to.window(driver.window_handles[-1])
    GenericPage(driver, url=URLS[1]).open()

    tabs.new_tab_by_button()
    driver.switch_to.window(driver.window_handles[-1])
    GenericPage(driver, url=URLS[2]).open()
    third_title = driver.title

    if move_option == MOVE_TO_END:
        driver.switch_to.window(driver.window_handles[0])
        expected_title = first_title
    else:
        expected_title = third_title

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
