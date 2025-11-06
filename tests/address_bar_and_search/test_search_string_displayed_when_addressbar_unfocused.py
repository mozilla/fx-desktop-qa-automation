import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.browser_object_panel_ui import PanelUi

TEXT = "Firefox"


@pytest.fixture()
def test_case():
    return "3028954"


def test_address_bar_and_search_string_displayed_when_addressbar_unfocused(
    driver: Firefox,
):
    """
    C3028954 - Search string is correctly displayed when the Address bar is unfocused
    """

    # Instantiate objects
    nav = Navigation(driver)
    panel_ui = PanelUi(driver)

    # Focus the address bar type a search string
    nav.type_in_awesome_bar(TEXT)

    # Click away in the page content and unfocus address bar
    panel_ui.unfocus_address_bar()

    # Check unfocused address bar containing a search string is displayed
    address_bar_text = nav.get_awesome_bar_text()
    assert address_bar_text == TEXT
