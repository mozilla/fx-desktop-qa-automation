import logging

from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

from modules.browser_object import Navigation, SearchBarContextMenu
from modules.page_object import GoogleSearch
from modules.util import Utilities


def test_login_form_copy_paste(driver: Firefox):
    pass


def test_text_area_copy_paste(driver: Firefox):
    pass


def test_search_field_copy_paste(driver: Firefox):
    Navigation(driver).open()
    context_menu = SearchBarContextMenu(driver)
    google_search = GoogleSearch(driver).open()
    util = Utilities()

    # send the text
    random_text = util.generate_random_text("sentence")
    search_bar = google_search.get_search_bar_element()
    search_bar.send_keys(random_text)
    logging.info(f"Sent the text {random_text} to the search bar.")

    # triple click the text to select all
    google_search.triple_click("search-bar-textarea")

    # context click
    context_menu.context_click_element(search_bar)
    with driver.context(driver.CONTEXT_CHROME):
        context_menu.get_context_item("context-menu-copy").click()
        google_search.hide_popup("contentAreaContextMenu")

    # delete the current text
    search_bar.send_keys(Keys.BACK_SPACE)

    # context click and paste the text back
    context_menu.context_click_element(search_bar)
    with driver.context(driver.CONTEXT_CHROME):
        context_menu.get_context_item("context-menu-paste").click()
        google_search.hide_popup("contentAreaContextMenu")

    # assert the value is correct
    assert search_bar.get_attribute("value") == random_text
