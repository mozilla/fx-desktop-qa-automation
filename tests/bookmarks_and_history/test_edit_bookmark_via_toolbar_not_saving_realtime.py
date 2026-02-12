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


def test_edit_bookmark_via_toolbar_not_saving_realtime(driver: Firefox):
    """
    C2090396 - Verify that Editing a Bookmark from the Bookmarks Toolbar will not save it in real time
    """

    # Instantiate objects
    nav = Navigation(driver)
    panel = PanelUi(driver)

    # Have at Least 1 Bookmark saved on the Bookmarks toolbar