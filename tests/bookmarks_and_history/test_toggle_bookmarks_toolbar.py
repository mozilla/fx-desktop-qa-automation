from time import sleep

import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation


@pytest.fixture()
def test_case():
    return "2084637"


def test_toggle_bookmark_toolbar(driver: Firefox):
    """
    C2084637: Verify that the user can Hide or Show the Bookmarks Toolbar using Keyboard shortcuts
    """
    # instantiate object
    nav = Navigation(driver).open()

    def is_bookmarks_toolbar_collapsed() -> str:
        with driver.context(driver.CONTEXT_CHROME):
            value = nav.get_element("bookmarks-toolbar").get_attribute("collapsed")
        return value

    # By default, the Bookmarks Toolbar is hidden.
    # The element attribute indicates whether the bookmarks toolbar is
    # either, collapsed = 'true' is hidden, or not collapsed 'false' is visible.
    assert is_bookmarks_toolbar_collapsed() == "true"

    # Un-hide the Bookmarks Toolbar with keyboard shortcut.
    nav.toggle_bookmarks_toolbar_with_key_combo()

    # Wait to ensure the Bookmarks Toolbar has time to change state
    sleep(0.5)
    assert is_bookmarks_toolbar_collapsed() == "false"

    # Toggle the Bookmarks Toolbar again and confirm it is hidden.
    nav.toggle_bookmarks_toolbar_with_key_combo()
    sleep(0.5)
    assert is_bookmarks_toolbar_collapsed() == "true"
