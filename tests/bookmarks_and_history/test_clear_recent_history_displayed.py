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
    panel_ui = PanelUi(driver)
    panel_ui.open()

    panel_ui.clear_recent_history(execute=False)
