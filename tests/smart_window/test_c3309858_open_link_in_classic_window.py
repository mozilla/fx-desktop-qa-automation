"""
C3309858 - Verify that the user can Open a link from a Smart Window to a Classic Window
"Open Link in New Window" on a link in a Smart Window opens a new Classic
Window showing the link.
"""

import pytest
from auto_fxui.browser_object import ContextMenu, SmartWindow
from auto_fxui.page_object import GenericPage
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

LINK = (By.ID, "lasagna-link")


@pytest.fixture()
def test_case():
    return "3309858"


def test_open_link_in_classic_window(
    driver: Firefox, active_smart_window: SmartWindow, tab_pages
):
    """
    C3309858 - Verify that the user can Open a link from a Smart Window to a Classic Window
    """
    # Instantiate objects
    page = GenericPage(driver, url=tab_pages(["recipe_links.html"])[0])
    context_menu = ContextMenu(driver)
    smart_window = active_smart_window

    page.open()

    existing_count = len(driver.window_handles)
    page.context_click(LINK)
    # The Smart Window menu has no "Classic Window" item: a plain new window is Classic.
    context_menu.click_and_hide_menu("context-menu-open-link-in-new-window")

    smart_window.wait_for_num_windows(existing_count + 1)
    smart_window.switch_to_new_window()
    smart_window.expect_smart_window_active(False)
    smart_window.expect_selected_tab_url_contains("lasagna.html")
