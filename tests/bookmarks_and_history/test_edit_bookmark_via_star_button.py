import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.browser_object_panel_ui import PanelUi
from modules.page_object_generics import GenericPage


URL_TO_EDIT = "https://www.mozilla.org/"
URL_TO_SAVE = "https://monitor.mozilla.org/"
BOOKMARK_NAME = "Mozilla Firefox"
BOOKMARK_LOCATION = "Other Bookmarks"


@pytest.fixture()
def test_case():
    return "2084549"


def test_edit_bookmark_via_star_button(driver: Firefox):
    """
    C2084549: Verify that the user can edit bookmark options from the star-shaped button,
    update name/location, and disable editor visibility on future bookmarks.
    """
    nav = Navigation(driver)
    panel = PanelUi(driver)
    edit_page = GenericPage(driver, url=URL_TO_EDIT)
    save_page = GenericPage(driver, url=URL_TO_SAVE)


    # Bookmark current tab using the star button
    edit_page.open()
    nav.add_bookmark_via_star_icon()

    # Edit the bookmark from the blue star and update details
    nav.click_on("blue-star-button")
    panel.edit_bookmark_details(
        name=BOOKMARK_NAME,
        tags="",
        location=BOOKMARK_LOCATION
    )

    # Verify bookmark details
    panel.verify_bookmark_in_toolbar(
        name=BOOKMARK_NAME,
        location=BOOKMARK_LOCATION
    )

    # Disable 'show editor when saving'
    panel.disable_editor_when_saving_bookmarks()

    # Bookmark a second page and confirm the editor is not shown
    save_page.open()
    nav.click_on("star-button")
    nav.element_not_visible("edit-bookmark-panel")
