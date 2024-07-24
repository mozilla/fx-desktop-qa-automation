import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, PanelUi
from modules.page_object import AboutPrefs, GenericPage, GoogleSearch
from modules.util import BrowserActions


@pytest.mark.unstable
def test_cookies_not_saved_private_browsing(driver: Firefox, screenshot):
    """
    C101677: ensure that cookies are not saved after using private browsing
    """
    # instantiate objs
    about_prefs = AboutPrefs(driver, category="privacy")
    panel_ui = PanelUi(driver).open()
    nav = Navigation(driver)
    google_search = GoogleSearch(driver)
    ba = BrowserActions(driver)

    # open new private window
    panel_ui.open_private_window()
    nav.switch_to_new_window()

    # open the google page and perform a search
    screenshot("1")
    google_search.open()
    google_search.type_in_search_bar("hello")
    google_search.press_enter_search_bar()
    google_search.wait_for_page_to_load()

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
