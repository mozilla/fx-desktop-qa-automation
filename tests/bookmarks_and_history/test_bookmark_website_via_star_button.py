from selenium.webdriver import Firefox
from modules.browser_object_navigation import Navigation
from modules.browser_object_panel_ui import PanelUi

URL_TO_BOOKMARKED = "https://www.mozilla.org/"


def test_bookmark_website_via_star(driver: Firefox):
    """
    C2084539: Verify that the Websites can be bookmarked via star-shaped button
    """
    # instantiate object
    nav = Navigation(driver)
    panel = PanelUi(driver)

    # Bookmark the given website and check the bookmark star turned blue
    driver.get(URL_TO_BOOKMARKED)
    with driver.context(driver.CONTEXT_CHROME):
        nav.get_element("star-button").click()
        nav.get_element("save-bookmark-button").click()
        assert nav.get_element("blue-star-button").is_displayed()

    # Verify that the bookmark is displayed in bookmarks menu
    panel.open_bookmarks_menu()
    with driver.context(driver.CONTEXT_CHROME):
        assert panel.get_element("mozilla-bookmarked").is_displayed()