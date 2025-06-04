import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.page_object_generics import GenericPage


@pytest.fixture()
def test_case():
    return "2084549"


BOOKMARK_URL_TO_EDIT = "https://www.mozilla.org/"
BOOKMARK_URL_TO_SAVE = "https://monitor.mozilla.org/"
BOOKMARK_NAME = "Mozilla Firefox"
BOOKMARK_LOCATION = "Other Bookmarks"


def test_edit_bookmark_via_star_button(driver: Firefox):
    """
    C2084549: Verify that the user can Edit a Bookmark options from the Star-shaped button
    """
    # Instantiate objects
    nav = Navigation(driver)
    first_page = GenericPage(driver, url=BOOKMARK_URL_TO_EDIT)
    second_page = GenericPage(driver, url=BOOKMARK_URL_TO_SAVE)

    # Bookmark using star button
    first_page.open()
    nav.add_bookmark_via_star_icon()

    # Open the edit bookmark panel via star button and change bookmark name and location
    nav.edit_bookmark_via_star_button(
        new_name=BOOKMARK_NAME, location=BOOKMARK_LOCATION
    )

    # Check bookmark name and location are changed in the bookmarks toolbar
    nav.verify_bookmark_exists_in_toolbar_other_bookmarks_folder(BOOKMARK_NAME)

    # Toggle "show editor when saving" setting
    nav.toggle_show_editor_when_saving()

    # Verify that panel isn't displayed when bookmarking a new website
    second_page.open()
    nav.verify_edit_bookmark_panel_not_visible_after_navigation()
