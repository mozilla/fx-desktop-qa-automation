from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.browser_object_panel_ui import PanelUi
from modules.browser_object_tabbar import TabBar
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

URL_TO_BOOKMARK = "https://www.mozilla.org/"


def test_open_bookmarks_from_toolbar(driver: Firefox):
    """
    C2084550: Verify that the user can open Bookmarks from the Toolbar with a mouse click
    """
    # instantiate object
    nav = Navigation(driver)
    panel = PanelUi(driver)
    newtab = TabBar(driver)

    # Bookmark the given website
    driver.get(URL_TO_BOOKMARK)
    with driver.context(driver.CONTEXT_CHROME):
        nav.get_element("star-button").click()
        nav.get_element("save-bookmark-button").click()

        # Open new tab and click on the bookmark from the Bookmarks Toolbar
        newtab.new_tab_by_button()
        panel.get_element("bookmark-by-title", labels=["Internet for people"]).click()

    # Verify that the page is loaded
    WebDriverWait(driver, 10).until(EC.title_is("Internet for people, not profit — Mozilla (US)"))