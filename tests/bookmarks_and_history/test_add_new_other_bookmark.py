from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, Navigation
from modules.page_object import GenericPage

BOOKMARK_URL = "about:robots"


def test_add_new_other_bookmark(driver: Firefox):
    """
    C2084518: verify user can add another bookmark from other bookmarks
    """
    nav = Navigation(driver)
    GenericPage(driver, url=BOOKMARK_URL).open()
    context_menu = ContextMenu(driver)

    # create a bookmark for other
    nav.bookmark_page_other()

    # get other bookmarks
    with driver.context(driver.CONTEXT_CHROME):
        nav.get_element("other-bookmarks").click()
        nav.context_click("other-bookmarks-popup")
        context_menu.get_element("context-menu-add-bookmark").click()

        context_menu.hide_popup_by_child_node("context-menu-add-bookmark")
        nav.hide_popup("OtherBookmarksPopup")

    # while 1:
    #     pass
