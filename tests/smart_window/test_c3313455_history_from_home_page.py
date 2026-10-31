"""
C3313455 - Reach the History page from the Smart Window Home page
"""

import pytest
from auto_fxui.browser_object import SmartBar, SmartWindow, TabBar
from selenium.webdriver import Firefox

URL = "https://www.mozilla.org/"


@pytest.fixture()
def test_case():
    return "3313455"


def test_history_from_home_page(driver: Firefox, active_smart_window: SmartWindow):
    """
    C3313455 - Reach the History page from the Smart Window Home page
    """
    # Give History something to show.
    driver.get(URL)
    TabBar(driver).expect_title_contains("Internet for people")

    bar = SmartBar(driver)
    bar.open_full_page_chat()
    bar.click_footer_button("smartwindow-footer-history")

    active_smart_window.expect_selected_tab_url_contains("about:firefoxview")
    active_smart_window.expect_selected_tab_url_contains("history")
