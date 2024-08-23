from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.browser_object_panel_ui import PanelUi
from modules.page_object_generics import GenericPage

URL_TO_BOOKMARK = "https://www.mozilla.org/"
URL_TO_SAVE = "https://monitor.mozilla.org/"
ENABLE_ADD_TAG = '''
            PlacesUtils.tagging.tagURI(makeURI("https://www.github.com"), ["tag1"]);
        '''


def test_edit_bookmark_from_bookmark_menu(driver: Firefox):
    """
    C2084490: Verify that the user can Edit a Bookmark from Bookmarks menu
    """
    # instantiate object
    nav = Navigation(driver)
    panel = PanelUi(driver)

    # Bookmark the given website via bookmarks menu
    GenericPage(driver, url=URL_TO_BOOKMARK).open()
    panel.open_bookmarks_menu()
    with driver.context(driver.CONTEXT_CHROME):
        panel.get_element("bookmark-current-tab").click()
        nav.get_element("save-bookmark-button").click()

        # enable add a tag to a bookmark in the bookmark panel
        driver.execute_script(ENABLE_ADD_TAG)

        # Open the Hamburger menu, click on the Edit This Bookmark button from the Bookmarks section
        panel.open_bookmarks_menu()
        panel.get_element("bookmark-current-tab").click()

        # Change bookmark name, location and add a tag
        nav.get_element("edit-bookmark-panel").send_keys("Mozilla Firefox")
        panel.get_element("bookmark-tags").send_keys("Work, To do")
        panel.get_element("bookmark-location").click()
        panel.get_element("other-bookmarks").click()
        nav.get_element("save-bookmark-button").click()

        # Check bookmark name and location are changed in the bookmarks toolbar
        panel.get_element("other-bookmarks-toolbar").click()
        panel.element_visible("other-bookmarks-by-title", labels=["Mozilla Firefox"])
        panel.get_element("other-bookmarks-toolbar").click()

        # Check tags are correctly added and checked
        nav.get_element("star-button").click()
        panel.get_element("extend-bookmark-tags").click()
        work_checkbox = panel.get_element("work-tag")
        work_checked_attr = work_checkbox.get_attribute("checked")
        assert work_checked_attr is None
        todo_checkbox = panel.get_element("todo-tag")
        todo_checked_attr = todo_checkbox.get_attribute("checked")
        assert todo_checked_attr is None
