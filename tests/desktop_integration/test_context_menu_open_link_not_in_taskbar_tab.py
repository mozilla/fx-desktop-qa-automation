import pytest
from auto_fxui.browser_object import ContextMenu, Navigation
from auto_fxui.page_object import GenericPage
from selenium.webdriver import Firefox

WIKIPEDIA_URL = "https://www.wikipedia.org/"
IN_SCOPE_URL_PART = "en.wikipedia.org"
MENU_ITEMS = [
    ("context-menu-open-link-in-tab", False),
    ("context-menu-open-link-in-new-window", False),
    ("context-menu-open-link-in-new-private-window", True),
]


@pytest.fixture()
def test_case():
    return "3814261"


@pytest.mark.parametrize(
    "menu_item, is_private",
    MENU_ITEMS,
    ids=["new_tab", "new_window", "private_window"],
)
def test_context_menu_open_link_not_in_taskbar_tab(
    driver: Firefox, menu_item: str, is_private: bool
):
    """
    C3814261 - Verify that opening a link in new tab/new window/in private browsing will open a new tab/window/private browsing window and NOT a web app window
    """

    # Instantiate objects
    nav = Navigation(driver)
    context_menu = ContextMenu(driver)
    wikipedia = GenericPage(driver, url=WIKIPEDIA_URL).open()

    # Click the "Add tab to taskbar" button, the tab moves into a Taskbar Tabs window
    nav.click_on("taskbar-tabs-button")
    nav.wait_for_taskbar_tab_window()

    # Right-click an in scope link and open it from the context menu
    wikipedia.context_click("wiki-english-link")
    context_menu.click_and_hide_menu(menu_item)

    # The link opens in a new window that is not a Taskbar Tabs window
    nav.wait_for_num_windows(2)
    nav.switch_to_new_window()
    wikipedia.url_contains(IN_SCOPE_URL_PART)
    nav.element_does_not_exist("taskbar-tab-window-root")
    if is_private:
        nav.is_private()
    else:
        nav.is_not_private()
