import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.browser_object_panel_ui import PanelUi
from modules.page_object_generics import GenericPage


@pytest.fixture()
def test_case():
    return "2084549"


URL_TO_EDIT = "https://www.mozilla.org/"
URL_TO_SAVE = "https://monitor.mozilla.org/"


def test_edit_bookmark_via_star_button(driver: Firefox):
    """
    C2084549: Verify that the user can Edit a Bookmark options from the Star-shaped button
    """
    # instantiate object
    nav = Navigation(driver)
    panel = PanelUi(driver)

    # Bookmark the given website and open the edit bookmark panel
    GenericPage(driver, url=URL_TO_EDIT).open()
    with driver.context(driver.CONTEXT_CHROME):
        nav.get_element("star-button").click()
        nav.get_element("save-bookmark-button").click()

        # Change bookmark name and location
        nav.get_element("star-button").click()
        nav.get_element("edit-bookmark-panel").send_keys("Mozilla Firefox")
        panel.get_element("bookmark-location").click()
        panel.get_element("other-bookmarks").click()
        nav.get_element("save-bookmark-button").click()

        # Check bookmark name and location are changed in the bookmarks toolbar
        panel.get_element("other-bookmarks-toolbar").click()
        panel.element_visible("other-bookmarks-by-title", labels=["Mozilla Firefox"])
        panel.get_element("other-bookmarks-toolbar").click()

        # Uncheck show editor when saving and verify that panel isn't displayed when bookmark a new website
        nav.get_element("star-button").click()
        panel.get_element("show-editor-when-saving-checkbox").click()
        nav.get_element("save-bookmark-button").click()
    GenericPage(driver, url=URL_TO_SAVE).open()
    with driver.context(driver.CONTEXT_CHROME):
        nav.get_element("star-button").click()
        nav.element_not_visible("edit-bookmark-panel")
