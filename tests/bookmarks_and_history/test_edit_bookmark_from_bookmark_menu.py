import time

import pytest
from selenium.webdriver import Firefox
from modules.browser_object_navigation import Navigation
from modules.browser_object_panel_ui import PanelUi
from modules.page_object_generics import GenericPage


@pytest.fixture()
def test_case():
    return "2084490"


URL_TO_BOOKMARK = "https://www.mozilla.org/"
URL_TO_SAVE = "https://monitor.mozilla.org/"
ENABLE_ADD_TAG = """
            PlacesUtils.tagging.tagURI(makeURI("https://www.github.com"), ["tag1"]);
        """


def test_edit_bookmark_from_bookmark_menu(driver: Firefox):
    """
    C2084490: Verify that the user can Edit a Bookmark from Bookmarks menu
    """
    # Instantiate object
    nav = Navigation(driver)
    panel = PanelUi(driver)
    page = GenericPage(driver, url=URL_TO_BOOKMARK)

    # Bookmark the given website via bookmarks menu
    page.open()
    panel.open_bookmarks_panel_from_hamburger_menu()
    panel.bookmark_current_tab_via_hamburger_menu()

    # Enable bookmark tagging functionality
    nav.enable_bookmark_tagging()

    # Open bookmark for editing via hamburger menu
    panel.open_bookmarks_panel_from_hamburger_menu()

    panel.prepare_bookmark_for_editing()

    # Change bookmark name, location and add a tag
    panel.edit_bookmark_details(
        name="Mozilla Firefox",
        tags="Work, To do",
        location="Other Bookmarks"
    )

    # Click the blue star button
    nav.click_on("blue-star-button")

    # Verify bookmark name and location in toolbar
    panel.verify_bookmark_in_toolbar("Mozilla Firefox", "Other Bookmarks")

    # Verify bookmark tags
    panel.verify_bookmark_tags(["Work", "To do"])
