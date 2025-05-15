import pytest
from selenium.webdriver import Firefox

from modules.browser_object_panel_ui import PanelUi
from modules.page_object_generics import GenericPage


@pytest.fixture()
def test_case():
    return "118806"


YOUTUBE_URL = "https://www.youtube.com/"


def test_opened_website_in_private_window_not_captured_in_history_list(driver: Firefox):
    """
    C118806 - Verify that opened websites in a New Private Window will not be displayed in the Hamburger submenu history
    """

    panel_ui = PanelUi(driver)
    panel_ui.open_and_switch_to_new_window("private")

    GenericPage(driver, url=YOUTUBE_URL).open()

    panel_ui.open_history_menu()

    with driver.context(driver.CONTEXT_CHROME):
        empty_label = panel_ui.get_element("recent-history-content").get_attribute(
            "value"
        )
        assert (
            empty_label == "(Empty)"
        ), f"Expected history to be empty, but found '{empty_label}'"
