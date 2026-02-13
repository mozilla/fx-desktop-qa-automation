import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.browser_object_panel_ui import PanelUi
from modules.util import BrowserActions


FOLDER_NAME = "Test Folder"
OLD_FOLDER_NAME = "New Folder"


@pytest.fixture()
def test_case():
    return "2090452"


@pytest.fixture()
def add_to_prefs_list():
    return [("browser.toolbars.bookmarks.visibility", "always")]


def test_edit_bookmark_folder_via_toolbar_not_saving_realtime(driver: Firefox):
    """
    C2090452 - Verify that Editing a Bookmarks folder from the Bookmarks Toolbar will not show changes in real time
    """

    # Instantiate objects
    nav = Navigation(driver)
    panel = PanelUi(driver)
    ba = BrowserActions(driver)

    # Right-click the Bookmarks toolbar and select Add Folder
    nav.add_folder_via_context_menu()

    # Click the Save button
    panel.save_folder_via_toolbar()

    # Right-click the bookmarks Folder and select Edit Folder
    nav.edit_bookmark_or_folder_via_context_menu_via_toolbar("folder")

    # Change the name of the folder and click outside of the panel
    panel.edit_folder_name_via_toolbar(FOLDER_NAME, ba)

    # The new modifications are not updated in real time on the Bookmarks Toolbar
    nav.verify_bookmark_exists_in_bookmarks_toolbar(OLD_FOLDER_NAME)

    # Click the Save button
    panel.save_folder_via_toolbar()

    # The Folder is displayed with the new name on the Bookmarks Toolbar
    nav.verify_bookmark_exists_in_bookmarks_toolbar(FOLDER_NAME)
