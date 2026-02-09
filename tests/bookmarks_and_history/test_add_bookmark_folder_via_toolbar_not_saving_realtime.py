from time import sleep

import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.browser_object_panel_ui import PanelUi


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

    # Right-click the Bookmarks toolbar and select Add Folder
    nav.add_folder_via_context_menu()

    # Edit the name of the folder and click outside of the panel
    with driver.context(driver.CONTEXT_CHROME):
        panel.get_element("edit-bookmark-panel").send_keys("New test bookmark")

