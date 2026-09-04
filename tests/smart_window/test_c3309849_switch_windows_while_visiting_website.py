"""
C3309849 - Switch windows while visiting a website
Verify that switching between Smart and Classic keeps the active tab and its
page loaded.
"""

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import TabBar
from modules.browser_object_smart_window import SmartWindow

URL = "about:robots"


@pytest.fixture()
def test_case():
    return "3309849"


def test_switch_windows_while_visiting_website(
    driver: Firefox, smart_window: SmartWindow
):
    """
    C3309849 - Switch windows while visiting a website
    """
    tabs = TabBar(driver)
    driver.get(URL)
    tabs.expect_title_contains("Gort")

    smart_window.activate_smart_window()

    # The page the user was on survives the switch to Smart.
    assert driver.current_url == URL
    tabs.expect_title_contains("Gort")

    smart_window.switch_to_classic_window()

    # ...and the switch back to Classic.
    assert driver.current_url == URL
    tabs.expect_title_contains("Gort")
