import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, PanelUi
from modules.page_object import AboutPrefs, GenericPage
from modules.util import BrowserActions


@pytest.mark.unstable
def test_cookies_not_saved_private_browsing(driver: Firefox):
    """
    C101677: ensure that cookies are not saved after using private browsing
    """
    # instantiate objs
    about_prefs = AboutPrefs(driver, category="privacy")
    panel_ui = PanelUi(driver).open()
    nav = Navigation(driver)
    wiki_page = GenericPage(
        driver, url="https://ro.wikipedia.org/wiki/Pagina_principal%C4%83"
    )
    ba = BrowserActions(driver)

    # open new private window
    panel_ui.open_private_window()
    nav.switch_to_new_window()

    # open the wiki page and perform a search
    wiki_page.open()
    wiki_search_bar = wiki_page.get_element("wiki-search-bar")
    wiki_search_bar.send_keys("hello")
    wiki_page.get_element("wiki-search-button").click()
    wiki_page.wait_for_page_to_load()

    # close the page and switch to first tab
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    about_prefs.open()

    # get the cookies
    about_prefs.get_element("cookies-manage-data").click()
    iframe = about_prefs.get_iframe()
    ba.switch_to_iframe_context(iframe)

    # wait for no children listed in the cookies menu
    about_prefs.wait_for_no_children("cookies-manage-data-sitelist")
