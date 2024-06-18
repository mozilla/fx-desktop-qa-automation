from time import sleep

from selenium.webdriver import Firefox

from modules.browser_object import ContextMenu, Navigation
from modules.page_object import GoogleSearch
from modules.util import Utilities


def test_login_form_copy_paste(driver: Firefox):
    pass


def test_text_area_copy_paste(driver: Firefox):
    pass


def test_search_field_copy_paste(driver: Firefox):
    nav = Navigation(driver).open()
    context_menu = ContextMenu(driver)
    google_search = GoogleSearch(driver).open()
    util = Utilities()

    # send the text
    random_text = util.generate_random_text("sentence")
    search_bar = google_search.get_search_bar_element()
    search_bar.send_keys()

    # google_search.type_in_search_bar(random_text)
    # google_search.triple_click("search-bar-textarea")

    # google_search.context_click_element()
