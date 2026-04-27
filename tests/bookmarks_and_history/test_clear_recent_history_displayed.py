import pytest
from selenium.webdriver import Firefox

from modules.browser_object import PanelUi


@pytest.fixture()
def test_case():
    return "172043"


def test_clear_recent_history_displayed(driver: Firefox):
    """
    C172043: Clear recent history panel displayed
    """
    # Instantiate object
    panel = PanelUi(driver)

    # Open Clear recent history dialog
    panel.open_history_menu()
    panel.open_clear_history_dialog()
