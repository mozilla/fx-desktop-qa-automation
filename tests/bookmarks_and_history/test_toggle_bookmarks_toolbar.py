import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation


@pytest.fixture()
def test_case():
    return "2084637"


@pytest.fixture()
def add_to_prefs_list():
    return [("browser.toolbars.bookmarks.visibility", "never")]


def test_toggle_bookmark_toolbar(driver: Firefox):
    """
    C2084637: Verify that the user can Hide or Show the Bookmarks Toolbar using Keyboard shortcuts
    """
    # Instantiate the object
    nav = Navigation(driver)

    # By default, the Bookmarks Toolbar is hidden. The element attribute indicates
    # whether the bookmarks toolbar is either, collapsed = 'true' is hidden,
    # or not collapsed = 'false' is visible.
    nav.expect_bookmarks_toolbar_visibility(expected=False)

    # Un-hide the Bookmarks Toolbar with keyboard shortcut.
    nav.toggle_bookmarks_toolbar_with_key_combo()
    nav.expect_bookmarks_toolbar_visibility(expected=True)

    # Toggle the Bookmarks Toolbar again and confirm it is hidden.
    nav.toggle_bookmarks_toolbar_with_key_combo()
    nav.expect_bookmarks_toolbar_visibility(expected=False)
