import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation
from modules.browser_object_panel_ui import PanelUi


@pytest.fixture()
def test_case():
    return "101665"


def test_websites_visited_in_private_browser_not_displayed_in_awesome_bar(
    driver: Firefox, nav: Navigation, panel_ui: PanelUi, websites
):
    """
    C101665 - Verify the visited websites from the Private Browsing session are not displayed inside the normal session
    Awesome Bar
    """

    initial_window_handle = driver.current_window_handle

    panel_ui.open_and_switch_to_new_window("private")

    for url in websites:
        driver.get(url)

    driver.switch_to.window(initial_window_handle)

    for url in websites:
        nav.type_in_awesome_bar(url)
        nav.verify_result_term(url)
        nav.clear_awesome_bar()
