import pytest
from selenium.webdriver import Firefox

from modules.browser_object_panel_ui import PanelUi
from modules.page_object_generics import GenericPage


@pytest.fixture()
def test_case():
    return "2084489"


URL_TO_BOOKMARK = "https://www.mozilla.org/"
BOOKMARK_TITLE = "Internet for people"


def test_bookmark_via_hamburger_menu(driver: Firefox):
    """
    C2084489: Verify that the user can bookmark a page using Bookmark current tab .. opened from Hamburger Menu
    """
    # Instantiate object
    panel = PanelUi(driver)
    page = GenericPage(driver, url=URL_TO_BOOKMARK)

    # Navigate to test website
    page.open()

    # Bookmark using Bookmark current tab option from Hamburger Menu
    panel.open_bookmarks_panel_from_hamburger_menu()
    panel.bookmark_current_tab_via_hamburger_menu()

    # Verify bookmark appears in Hamburger Menu, Bookmarks section
    panel.open_bookmarks_panel_from_hamburger_menu()
    panel.verify_bookmark_exists_in_hamburger_menu(BOOKMARK_TITLE)
