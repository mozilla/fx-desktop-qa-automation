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
    gen_page = GenericPage(driver)
    panel_ui = PanelUi(driver)
    panel_ui.open()
    panel_ui.open_history_menu()

    panel_ui.select_clear_history_option("Everything")

    gen_page.click_on("clear-history-button")
    panel_ui.confirm_history_clear()
