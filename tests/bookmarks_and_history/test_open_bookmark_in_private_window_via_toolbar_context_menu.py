import pytest
from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, Navigation, PanelUi, TabBar
from modules.page_object_generics import GenericPage


@pytest.fixture()
def test_case():
    return "2084553"


BOOKMARK_URL = "https://www.mozilla.org/"
BOOKMARK_TITLE = "Internet for people"


def test_open_bookmark_in_new_private_window_via_toolbar_context_menu(driver: Firefox):
    """
    C2084553: Verify that a bookmarked page can be open in a New Private Window from Toolbar context menu.
    """

    # Instantiate objects
    nav = Navigation(driver)
    tabs = TabBar(driver)
    page = GenericPage(driver, url=BOOKMARK_URL)

    # Bookmark the test page via star button
    page.open()
    nav.add_bookmark_via_star_icon()

    # In a new tab, right-click the bookmarked page in the toolbar and select 'Open in New Private Window' from the
    # context menu
    tabs.new_tab_by_button()
    nav.open_bookmark_in_new_private_window_via_context_menu(BOOKMARK_TITLE)

    # Verify that the test page is opened in a new private window
    tabs.wait_for_num_tabs(3)
    driver.switch_to.window(driver.window_handles[-1])
    assert nav.is_private()

    page.url_contains("mozilla")
