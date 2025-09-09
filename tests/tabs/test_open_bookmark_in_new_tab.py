import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from modules.browser_object import Navigation, TabBar
from modules.page_object_generics import GenericPage


@pytest.fixture()
def test_case():
    return "134460"


BOOKMARK_URL = "https://www.youtube.com/"
BOOKMARK_TITLE = "YouTube"


def test_open_bookmark_in_new_tab(driver: Firefox):
    """
    C134460: Verify that New Tabs can be opened by right clicking and selecting new tab from the bookmarks.
    """

    # Instantiate objects
    nav = Navigation(driver)
    tabs = TabBar(driver)
    page = GenericPage(driver, url=BOOKMARK_URL)

    # Bookmark the test page via star button
    page.open()
    nav.add_bookmark_via_star_icon()

    # In a new tab, right-click the bookmarked page in the toolbar and select Open in New Tab from the context menu
    tabs.new_tab_by_button()
    tabs.wait_for_num_tabs(2)
    nav.open_bookmark_in_new_tab_via_context_menu(BOOKMARK_TITLE)

    # Verify that the test page is opened in a new normal tab
    tabs.wait_for_num_tabs(3)
    driver.switch_to.window(driver.window_handles[-1])

    WebDriverWait(driver, 5).until(EC.url_contains("youtube"))
    assert "youtube" in driver.current_url
    page.url_contains("youtube")
