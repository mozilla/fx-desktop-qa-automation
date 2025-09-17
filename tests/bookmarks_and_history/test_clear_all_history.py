import pytest
from selenium.webdriver import Firefox

from modules.browser_object import PanelUi
from modules.page_object import GenericPage


@pytest.fixture()
def test_case():
    return "172045"


@pytest.fixture()
def use_profile():
    return "theme_change"


def test_clear_all_history(driver: Firefox):
    """
    C172045: Verify that the user can Clear all the History
    """
    # Instantiate objects
    page = GenericPage(driver)
    panel = PanelUi(driver)

    # Open Clear History dialog
    panel.open_history_menu()
    panel.open_clear_history_dialog()

    # Select the option to clear all the history
    panel.select_history_time_range_option("Everything")
    # A method in panel BOM  with selectors moved accordingly would make more sense, I'll come to this later,
    # there are some context switching + iframe entanglements, couldn't make it work so far
    page.click_on("clear-history-button")

    # Verify all the history is deleted
    panel.confirm_history_clear()
