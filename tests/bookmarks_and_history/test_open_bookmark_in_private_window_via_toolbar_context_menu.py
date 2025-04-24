import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, Navigation, PanelUi, TabBar
from modules.page_object_generics import GenericPage


@pytest.fixture()
def test_case():
    return "2084553"


URL_TO_BOOKMARK = "https://www.mozilla.org/"


def test_open_bookmark_in_new_private_window_via_toolbar_context_menu(driver: Firefox):
    """
    C2084553: Verify that a bookmarked page can be open in a New Private Window from Toolbar context menu.
    """

    # Instantiate object
    nav = Navigation(driver)
    panel = PanelUi(driver)
    tabs = TabBar(driver)
    context_menu = ContextMenu(driver)
    page = GenericPage(driver, url=URL_TO_BOOKMARK)

    # Bookmark the test page via star button
    page.open()
    nav.add_bookmark_via_star_icon()

    # In a new tab, right-click the bookmarked page in the toolbar and select 'Open in New Private Window' from the
    # context menu
    with driver.context(driver.CONTEXT_CHROME):
        tabs.new_tab_by_button()
        panel.element_clickable("bookmark-by-title", labels=["Internet for people"])
        panel.context_click("bookmark-by-title", labels=["Internet for people"])
        context_menu.click_and_hide_menu(
            "context-menu-toolbar-open-in-new-private-window"
        )

    # Verify that the test page is opened in a new private window
    tabs.wait_for_num_tabs(3)
    driver.switch_to.window(driver.window_handles[-1])
    assert nav.is_private()

    page.url_contains("mozilla")
