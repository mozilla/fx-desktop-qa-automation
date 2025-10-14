import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, TabBar


TABS_TO_OPEN = 4
FIRST_URL = "about:about"
SECOND_URL = "about:robots"

@pytest.fixture()
def test_case():
    return "134648"


def test_reopen_tab_through_context_menu(driver: Firefox):
    """C134648: Reopen tab through context menu"""

    # Instantiate objects
    tabs = TabBar(driver)
    tab_context_menu = ContextMenu(driver)

    # Open several different tabs and close them
    driver.get(FIRST_URL)
    for _ in range(1, TABS_TO_OPEN):
        tabs.new_tab_by_button()
    driver.switch_to.window(driver.window_handles[-1])
    driver.get(SECOND_URL)
    remaining_tab = tabs.get_tab(1)
    closing_tab = tabs.get_tab(TABS_TO_OPEN)

    assert tabs.get_tab_title(closing_tab).startswith("Gort")

    driver.close()
    driver.switch_to.window(driver.window_handles[0])

    # Right click on the remaining tab and reopen previously closed tab
    tabs.context_click(remaining_tab)
    tab_context_menu.click_and_hide_menu("context-menu-reopen-closed-tab")

    reopened_tab = tabs.get_tab(TABS_TO_OPEN + 1)
    assert tabs.get_tab_title(reopened_tab).startswith("Gort")
