"""
C3309857 - Verify that the user can Open a link from a Classic Window to a Smart Window
"Open Link in New Smart Window" on a link in a Classic Window opens a new
Smart Window showing the link.
"""

import pytest
from auto_fxui.browser_object import SmartWindow
from auto_fxui.page_object import GenericPage
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

LINK = (By.ID, "lasagna-link")


@pytest.fixture()
def test_case():
    return "3309857"


def test_open_link_in_smart_window(
    driver: Firefox, smart_window: SmartWindow, tab_pages
):
    """
    C3309857 - Verify that the user can Open a link from a Classic Window to a Smart Window
    """
    page = GenericPage(driver, url=tab_pages(["recipe_links.html"])[0])

    page.open()
    smart_window.expect_smart_window_active(False)

    existing_count = len(driver.window_handles)
    page.context_click(LINK)
    smart_window.click_and_hide_menu("context-open-link-in-smart-window")

    smart_window.wait_for_num_windows(existing_count + 1)
    smart_window.switch_to_new_window()
    smart_window.expect_smart_window_active(True)
    smart_window.expect_selected_tab_url_contains("lasagna.html")
