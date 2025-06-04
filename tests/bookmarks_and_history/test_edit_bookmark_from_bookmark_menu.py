import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.browser_object_panel_ui import PanelUi
from modules.page_object_generics import GenericPage


@pytest.fixture()
def test_case():
    return "2084490"


BOOKMARK_URL = "https://www.mozilla.org/"
BOOKMARK_NAME = "Mozilla Firefox"
BOOKMARK_LOCATION = "Other Bookmarks"
BOOKMARK_TAGS_STR = "Work, To do"
BOOKMARK_TAGS_LIST = ["Work", "To do"]


def test_edit_bookmark_from_bookmark_menu(driver: Firefox):
    """
    C2084490: Verify that the user can Edit a Bookmark from Bookmarks menu
    """
    # Instantiate objects
    nav = Navigation(driver)
    panel = PanelUi(driver)
    page = GenericPage(driver, url=BOOKMARK_URL)

    # Bookmark using Bookmark current tab option from Hamburger Menu
    page.open()
    panel.open_bookmarks_panel_from_hamburger_menu()
    panel.bookmark_current_tab_via_hamburger_menu()

    # Enable bookmark tagging functionality
    panel.enable_bookmark_tagging()

    # Edit bookmark details via Hamburger Menu
    panel.edit_bookmark_from_hamburger_menu(
        new_name=BOOKMARK_NAME, tags=BOOKMARK_TAGS_STR, location=BOOKMARK_LOCATION
    )

    # Verify bookmark was moved to Other Bookmarks with correct name
    nav.verify_bookmark_exists_in_toolbar_other_bookmarks_folder(BOOKMARK_NAME)

    # Verify bookmark tags are set correctly
    actual_tags = panel.get_bookmark_tags(BOOKMARK_TAGS_LIST)
    assert actual_tags == BOOKMARK_TAGS_LIST
