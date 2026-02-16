import time

import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.browser_object_panel_ui import PanelUi
from modules.classes.bookmark import Bookmark
from modules.util import BrowserActions

BOOKMARK = Bookmark(url="mozilla.org", name="Mozilla", tags="M", keyword="Mozz")
BOOKMARK_DEFAULT_NAME = "New Bookmark"
BOOKMARK_NAME = "Mozilla"


@pytest.fixture()
def test_case():
    return "2090393"


def test_add_bookmark_via_toolbar_not_saving_realtime(driver: Firefox):
    """
    C2090393 - Verify that adding a Bookmark from the Bookmarks toolbar is not saved in real time
    """

    # Instantiate objects
    nav = Navigation(driver)
    ba = BrowserActions(driver)
    panel = PanelUi(driver)

    # Right-click the Bookmarks Toolbar and select Add Bookmark
    nav.add_bookmark_or_folder_via_context_menu_via_toolbar()

    # The New Bookmark is not displayed on the Bookmarks Toolbar
    nav.verify_bookmark_not_in_bookmarks_toolbar(BOOKMARK_DEFAULT_NAME)

    # Add any text to each field
    nav.add_bookmark_via_toolbar_other_bookmark_context_menu(BOOKMARK, ba, save=False)

    # Click out-side of the add fields
    panel.click_outside_add_folder_panel()

    # Add time sleep, the assert may always pass because the panel hasn’t had time to close yet
    time.sleep(1)

    # The Bookmark folder is not created and add folder panel isn't dismissed
    assert panel.is_add_folder_panel_open()

    # The New Bookmark is not displayed on the Bookmarks Toolbar
    nav.verify_bookmark_not_in_bookmarks_toolbar(BOOKMARK_DEFAULT_NAME)

    # Click on save button
    panel.save_folder_via_toolbar()

    # The bookmark is corectly created
    nav.verify_bookmark_exists_in_bookmarks_toolbar(BOOKMARK_NAME)