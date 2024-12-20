import pytest
from selenium.webdriver import Firefox

from modules.browser_object import PanelUi
from modules.page_object import GenericPage
from modules.util import BrowserActions


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
    panel_ui = PanelUi(driver).open()
    gen_page = GenericPage(driver)
    panel_ui.open_history_menu()
    ba = BrowserActions(driver)

    panel_ui.select_clear_history_option("Everything")

    gen_page.get_element("clear-history-button").click()
    ba.switch_to_content_context()

    panel_ui.open_history_menu()
    panel_ui.element_does_not_exist("bookmark-item")
    