import time

import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.browser_object_panel_ui import PanelUi
from modules.util import BrowserActions

FOLDER_NAME = "New Folder"


@pytest.fixture()
def test_case():
    return "2090451"


@pytest.fixture()
def add_to_prefs_list():
    return [("browser.toolbars.bookmarks.visibility", "always")]


def test_add_bookmark_folder_via_toolbar_not_saving_realtime(driver: Firefox):
    """
    C2090451 - Verify that adding a Bookmark Folder from the Bookmarks Toolbar will not save changes in real time
    """

    # Instantiate objects
    nav = Navigation(driver)
    panel = PanelUi(driver)
    ba = BrowserActions(driver)

    # Right-click the Bookmarks toolbar and select Add Folder
    nav.add_folder_via_context_menu()

    # Edit the name of the folder and click out-side of the panel
    panel.edit_bookmark_via_toolbar(FOLDER_NAME, ba)
    panel.click_outside_add_folder_panel()

    # Add time sleep, the assert may always pass because the panel hasn’t had time to close yet
    time.sleep(1)

    # The Bookmark folder is not created and add folder panel isn't dismissed
    assert panel.is_add_folder_panel_open()

    # Click the Save button
    panel.save_folder_via_toolbar()
    nav.verify_bookmark_exists_in_bookmarks_toolbar(FOLDER_NAME)
