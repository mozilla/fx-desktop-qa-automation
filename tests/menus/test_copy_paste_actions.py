import logging
from time import sleep

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

from modules.browser_object import ContextMenu
from modules.page_object import GoogleSearch
from modules.page_object_autofill import LoginAutofill, TextAreaFormAutofill
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "2264626"


@pytest.mark.ci
def test_login_form_copy_paste(driver: Firefox):
    """C2264626 - Verify that copy and paste actions are displayed in the context menu and work as expected"""
    # instantiate objects
    login_fill = LoginAutofill(driver).open()
    context_menu = ContextMenu(driver)
    util = Utilities()
    random_text = util.generate_random_text("sentence")

    # get the field and send text
    password_field = login_fill.get_element("input-field", labels=["current-password"])
    password_field.send_keys(random_text)
    logging.info(f"Sent the text {random_text} to the textarea.")

    # triple click and copy text
    login_fill.triple_click("input-field", labels=["current-password"])
    login_fill.context_click(password_field)
    context_menu.click_and_hide_menu("context-menu-copy")

    # delete all text
    password_field.send_keys(Keys.BACK_SPACE)
    assert password_field.get_attribute("value") == ""

    login_fill.context_click(password_field)
    context_menu.click_and_hide_menu("context-menu-paste")

    # final assertion
    assert password_field.get_attribute("value") != random_text


def test_text_area_copy_paste(driver: Firefox):
    # initialize objects
    text_area_fill = TextAreaFormAutofill(driver).open()
    util = Utilities()
    context_menu = ContextMenu(driver)
    text_area = text_area_fill.get_element("street-address-textarea")

    # send the text
    random_text = util.generate_random_text("sentence")
    text_area.send_keys(random_text)
    logging.info(f"Sent the text {random_text} to the textarea.")

    # copy the text
    text_area_fill.triple_click("street-address-textarea")
    text_area_fill.context_click(text_area)
    context_menu.click_and_hide_menu("context-menu-copy")

    # delete all the text and paste
    text_area.send_keys(Keys.BACK_SPACE)
    assert text_area.get_attribute("value") == ""

    text_area_fill.context_click(text_area)
    context_menu.click_and_hide_menu("context-menu-paste")

    # check value
    assert text_area.get_attribute("value") == random_text


def test_search_field_copy_paste(driver: Firefox):
    max_attempts = 5
    context_menu = ContextMenu(driver)
    google_search = GoogleSearch(driver)

    for attempt in range(1, max_attempts + 1):
        google_search.open()

        # Check for CAPTCHA after opening the page
        if "recaptcha" in driver.page_source.lower():
            logging.warning(f"CAPTCHA detected on attempt {attempt}. Retrying...")
            if attempt < max_attempts:
                driver.delete_all_cookies()
                driver.get("about:newtab")
                sleep(2)
                continue
            else:
                pytest.skip("CAPTCHA triggered repeatedly. Skipping test after 5 attempts.")

        # If no CAPTCHA, proceed with the test and break out of retry loop
        break

    util = Utilities()

    # send the text
    random_text = util.generate_random_text("sentence")
    search_bar = google_search.get_search_bar_element()
    search_bar.send_keys(random_text)
    logging.info(f"Sent the text {random_text} to the search bar.")

    # triple click the text to select all
    google_search.triple_click("search-bar-textarea")

    # context click
    google_search.context_click(search_bar)
    context_menu.click_and_hide_menu("context-menu-copy")

    # delete the current text
    search_bar.send_keys(Keys.BACK_SPACE)
    assert search_bar.get_attribute("value") == ""

    # context click and paste the text back
    google_search.context_click(search_bar)
    context_menu.click_and_hide_menu("context-menu-paste")

    # assert the value is correct
    assert search_bar.get_attribute("value") == random_text
