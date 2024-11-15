import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, Navigation, PanelUi, TabBar
from modules.page_object_generics import GenericPage


@pytest.fixture()
def test_case():
    return "2084552"


URL_TO_BOOKMARK = "https://www.mozilla.org/"


def test_open_bookmark_in_new_window_via_toolbar_context_menu(driver: Firefox):
    """
    C2084552: Verify that a bookmarked page can be open in a New Window from Toolbar context menu.
    """

    # Instantiate object
    nav = Navigation(driver)
    panel = PanelUi(driver)
    tabs = TabBar(driver)
    context_menu = ContextMenu(driver)
    page = GenericPage(driver, url=URL_TO_BOOKMARK).open()

    # Bookmark the test page via star button
    nav.add_bookmark_via_star()

    # In a new tab, right-click the bookmarked page in the toolbar and select 'Open in New Window' from the context menu
    with driver.context(driver.CONTEXT_CHROME):
        tabs.new_tab_by_button()
        bookmarked_page = panel.get_element(
            "bookmark-by-title", labels=["Internet for people"]
        )
        context_menu.context_click(bookmarked_page)
        context_menu.click_and_hide_menu("context-menu-toolbar-open-in-new-window")

    # Verify that the test page is opened in a new normal window
    driver.switch_to.window(driver.window_handles[-1])
    nav.element_not_visible("private-browsing-icon")
    page.url_contains("mozilla")
