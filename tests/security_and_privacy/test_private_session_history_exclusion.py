import pytest
from selenium.webdriver import Firefox

from modules.browser_object_panel_ui import PanelUi


@pytest.fixture()
def test_case():
    return "101663"


def test_websites_visited_in_private_browser_not_displayed_in_history(
    driver: Firefox, panel_ui: PanelUi, websites
):
    """
    C101663 - Verify the visited websites from the Private Browsing session are not displayed inside the normal session
    History menu
    """

    initial_window_handle = driver.current_window_handle

    panel_ui.open()
    panel_ui.open_and_switch_to_new_window("private")

    for url in websites:
        driver.get(url)
    driver.switch_to.window(initial_window_handle)
    panel_ui.confirm_history_clear()
