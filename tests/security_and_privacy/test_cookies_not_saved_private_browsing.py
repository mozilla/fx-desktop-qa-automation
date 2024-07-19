
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, PanelUi
from modules.page_object import AboutPrefs, GenericPage
from modules.util import BrowserActions


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

    # ensure none are listed
    sitelist = about_prefs.get_element("cookies-manage-data-sitelist")
    sites = about_prefs.get_all_children(sitelist)

    # note when there are 0 children, this is a bit slow
    assert len(sites) == 0
