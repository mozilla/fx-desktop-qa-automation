"""
C4120454 - Verify that the Smart Window is automatically restored when "Open previous windows and tabs" option is selected
With "Open previous windows and tabs" on, closing and starting Firefox brings
back both the Classic and the Smart window with their tabs.
"""

import pytest
from auto_fxui.browser_object import SmartWindow
from auto_fxui.restart import restart_firefox
from selenium.webdriver import Firefox


@pytest.fixture()
def test_case():
    return "4120454"


@pytest.fixture()
def fxa_env():
    """No FxA: the WAF bypass is installed in the Firefox that restart_firefox quits."""
    return None


@pytest.fixture()
def add_to_prefs_list():
    # 3 is "Open previous windows and tabs".
    return [("browser.startup.page", 3)]


def test_smart_window_auto_restored(
    driver: Firefox, smart_window: SmartWindow, tab_pages
):
    """
    C4120454 - Verify that the Smart Window is automatically restored when "Open previous windows and tabs" option is selected
    """
    classic_url, smart_url = tab_pages(["flights.html", "lasagna.html"])
    driver.get(classic_url)
    driver.switch_to.new_window("window")
    driver.get(smart_url)
    smart_window.activate_smart_window()
    smart_window.expect_smart_window_active(True)

    restart_firefox(driver)

    smart_window.expect(lambda _: len(smart_window.get_windows()) == 2)
    windows = {(w["smart"], tuple(w["urls"])) for w in smart_window.get_windows()}
    assert windows == {(False, (classic_url,)), (True, (smart_url,))}, windows
