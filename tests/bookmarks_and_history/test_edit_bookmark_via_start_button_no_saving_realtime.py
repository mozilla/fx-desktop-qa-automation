import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.browser_object_panel_ui import PanelUi
from modules.page_object_generics import GenericPage


BOOKMARK_URL = "https://www.mozilla.org/"
BOOKMARK_NAME = "Mozilla Firefox"
OLD_BOOKMARK_NAME = "Mozilla - Internet for people, not profit (US)"


@pytest.fixture()
def test_case():
    return "2090397"


def edit_bookmark_via_start_button_no_saving_realtime(driver: Firefox):
    """
    C2090397 - Verify that Editing a Bookmark from the Star button will not update it in real time
    """

    # Instantiate objects
    nav = Navigation(driver)
    page = GenericPage(driver, url=BOOKMARK_URL)
    panel = PanelUi(driver)

    # Have at Least 1 Bookmark saved on the Bookmarks toolbar
    page.open()
    nav.add_bookmark_via_star_icon()

    # Click the Star shaped button and edit bookmark
    nav.edit_bookmark_via_star_button(
        new_name=BOOKMARK_NAME, save_bookmark=False
    )

    # Click on the next field or somewhere inside the Edit Bookmarks panel
    panel.click_inside_bookmark_panel()

    # The Name displayed on the Bookmarks toolbar is not updated in real time when the user clicks a different field
    nav.verify_bookmark_exists_in_bookmarks_toolbar(OLD_BOOKMARK_NAME)

    # Click out-side of the Edit Bookmarks panel
    panel.click_outside_add_folder_panel()

    # The new Bookmark name is displayed on the Bookmarks toolbar
    nav.verify_bookmark_exists_in_bookmarks_toolbar(OLD_BOOKMARK_NAME)
