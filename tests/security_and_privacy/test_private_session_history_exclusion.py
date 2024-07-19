import pytest
from selenium.webdriver import Firefox

from modules.browser_object_panel_ui import PanelUi

YOUTUBE_URL = "https://www.youtube.com/"
FACEBOOK_URL = "https://www.facebook.com/"
AMAZON_URL = "https://www.amazon.com/"


@pytest.fixture()
def add_prefs():
    return []


def test_websites_visited_in_private_browser_not_displayed_in_history(driver: Firefox):
    """
    C101663 - Verify the visited websites from the Private Browsing session are not displayed inside the normal session
    History menu
    """

    initial_window_handle = driver.current_window_handle

    panel_ui = PanelUi(driver).open()
    panel_ui.open_private_window()
    panel_ui.switch_to_new_window()

    driver.get(YOUTUBE_URL)
    driver.get(FACEBOOK_URL)
    driver.get(AMAZON_URL)

    driver.switch_to.window(initial_window_handle)

    panel_ui.open_history_menu()
    with panel_ui.driver.context(panel_ui.driver.CONTEXT_CHROME):
        empty_label = panel_ui.get_element("recent-history-content").get_attribute(
            "value"
        )
        assert (
            empty_label == "(Empty)"
        ), f"Expected history to be empty, but found '{empty_label}'"
