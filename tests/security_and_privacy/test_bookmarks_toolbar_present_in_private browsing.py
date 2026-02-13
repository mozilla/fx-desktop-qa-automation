import pytest
from browser_object_panel_ui import PanelUi
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.browser_object_tabbar import TabBar


@pytest.fixture()
def test_case():
    return "2359323"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.privatebrowsing.felt-privacy-v1", True),
        ("browser.toolbars.bookmarks.visibility", "newtab"),
    ]


def test_bookmarks_toolbar_present_in_private_browsing(driver: Firefox):
    """
    C2359323 - Verify that the Bookmarks toolbar is displayed in a Private Window, if the preference is set to "Show
    in new tab"
    """
    # Instantiate objects
    nav = Navigation(driver)
    panel = PanelUi(driver)
    tabs = TabBar(driver)

    # Open a Private Window
    panel.open_and_switch_to_new_window("private")

    # Open a new tab and look for the Bookmark toolbar
    tabs.new_tab_by_button()
    tabs.switch_to_new_tab()

    # Verify the Bookmark toolbar is displayed
    nav.expect_bookmarks_toolbar_visibility(expected=True)
