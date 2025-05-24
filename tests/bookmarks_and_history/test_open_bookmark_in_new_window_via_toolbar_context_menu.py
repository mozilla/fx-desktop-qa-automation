import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, PanelUi, TabBar
from modules.page_object_generics import GenericPage


@pytest.fixture()
def test_case():
    return "2084552"


URL_TO_BOOKMARK = "https://www.mozilla.org/"
BOOKMARK_TITLE = "Internet for people"


def test_open_bookmark_in_new_window_via_toolbar_context_menu(driver: Firefox):
    """
    C2084552 - Verify that a bookmarked page can be open in a New Window from Toolbar context menu.
    """

    # Instantiate object
    nav = Navigation(driver)
    panel = PanelUi(driver)
    tabs = TabBar(driver)
    page = GenericPage(driver, url=URL_TO_BOOKMARK)

    # Bookmark the test page via star button
    page.open()
    nav.add_bookmark_via_star_icon()

    # In a new tab, right-click the bookmarked page in the toolbar and select Open in new Window from the context menu
    tabs.new_tab_by_button()
    panel.open_bookmark_in_new_window_via_context_menu(BOOKMARK_TITLE)

    # Verify that the test page is opened in a new normal Window
    tabs.wait_for_num_tabs(3)
    driver.switch_to.window(driver.window_handles[-1])
    assert not nav.is_private()
    page.url_contains("mozilla")
