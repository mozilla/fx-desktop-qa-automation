import logging

from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

from modules.browser_object import Navigation, SearchBarContextMenu
from modules.page_object import GoogleSearch
from modules.page_object_autofill_login import LoginAutofill
from modules.page_object_form_autofill_textarea import TextAreaFormAutofill
from modules.util import Utilities


def test_login_form_copy_paste(driver: Firefox):
    # instantiate objects
    login_fill = LoginAutofill(driver).open()
    context_menu = SearchBarContextMenu(driver)
    util = Utilities()
    random_text = util.generate_random_text("sentence")

    # get the field and send text
    password_field = login_fill.get_element(
        "login-input-field", labels=["current-password"]
    )
    password_field.send_keys(random_text)
    logging.info(f"Sent the text {random_text} to the textarea.")

    # triple click and copy text
    login_fill.triple_click("login-input-field", labels=["current-password"])
    context_menu.context_click(password_field)
    with driver.context(driver.CONTEXT_CHROME):
        context_menu.get_context_item("context-menu-copy").click()
        login_fill.hide_popup("contentAreaContextMenu")

    # delete all text
    password_field.send_keys(Keys.BACK_SPACE)
    assert password_field.get_attribute("value") == ""

    context_menu.context_click(password_field)
    with driver.context(driver.CONTEXT_CHROME):
        context_menu.get_context_item("context-menu-paste").click()
        login_fill.hide_popup("contentAreaContextMenu")

    # final assertion
    assert password_field.get_attribute("value") != random_text


def test_text_area_copy_paste(driver: Firefox):
    # initialize objects
    text_area_fill = TextAreaFormAutofill(driver).open()
    util = Utilities()
    context_menu = SearchBarContextMenu(driver)
    text_area = text_area_fill.get_element("street-address-textarea")

    # send the text
    random_text = util.generate_random_text("sentence")
    text_area.send_keys(random_text)
    logging.info(f"Sent the text {random_text} to the textarea.")

    # copy the text
    text_area_fill.triple_click("street-address-textarea")
    context_menu.context_click(text_area)
    with driver.context(driver.CONTEXT_CHROME):
        context_menu.get_context_item("context-menu-copy").click()
        text_area_fill.hide_popup("contentAreaContextMenu")

    # delete all the text and paste
    text_area.send_keys(Keys.BACK_SPACE)
    assert text_area.get_attribute("value") == ""

    context_menu.context_click(text_area)
    with driver.context(driver.CONTEXT_CHROME):
        context_menu.get_context_item("context-menu-paste").click()
        text_area_fill.hide_popup("contentAreaContextMenu")

    # check value
    assert text_area.get_attribute("value") == random_text


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
    context_menu.context_click(search_bar)
    with driver.context(driver.CONTEXT_CHROME):
        context_menu.get_context_item("context-menu-copy").click()
        google_search.hide_popup("contentAreaContextMenu")

    # delete the current text
    search_bar.send_keys(Keys.BACK_SPACE)
    assert search_bar.get_attribute("value") == ""

    # context click and paste the text back
    context_menu.context_click(search_bar)
    with driver.context(driver.CONTEXT_CHROME):
        context_menu.get_context_item("context-menu-paste").click()
        google_search.hide_popup("contentAreaContextMenu")

    # assert the value is correct
    assert search_bar.get_attribute("value") == random_text
