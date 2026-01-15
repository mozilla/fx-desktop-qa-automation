import logging
from time import sleep

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.keys import Keys

from modules.browser_object import ContextMenu
from modules.page_object import GoogleSearch, LoginAutofill, TextAreaFormAutofill
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "2264626"


def test_login_form_copy_paste(driver: Firefox):
    """
    C2264626 - Verify that copy and paste actions are displayed
    in the context menu and work as expected
    """

    # Instantiate objects
    login_fill = LoginAutofill(driver)
    login_fill.elements["input-field"]["groups"].append("doNotCache")
    login_fill.open()
    context_menu = ContextMenu(driver)
    util = Utilities()
    random_text = util.generate_random_text("word")
    random_other_text = util.generate_random_text("word")

    # Quick method for copy/paste
    def context_action(element_name, action="copy", labels=[]):
        login_fill.triple_click(element_name, labels=labels)
        login_fill.context_click(element_name, labels=labels)
        context_menu.click_and_hide_menu(f"context-menu-{action}")

    # Paste in the clear
    login_fill.fill("username-field", random_text, press_enter=False)
    context_action("username-field")
    login_fill.fill("username-field", random_other_text, press_enter=False)
    context_action("username-field", "paste")
    login_fill.element_attribute_contains("username-field", "value", random_text)

    # Paste to password
    login_fill.context_click("input-field", labels=["current-password"])
    context_menu.click_and_hide_menu("context-menu-paste")
    login_fill.context_click("input-field", labels=["current-password"])
    context_menu.click_and_hide_menu("context-menu-reveal-password")
    login_fill.element_attribute_contains(
        "input-field", "value", random_text, labels=["current-password"]
    )

    # Triple click and attempt to copy text from protected input
    login_fill.fill(
        "input-field", random_other_text, labels=["current-password"], press_enter=False
    )
    context_action("input-field", labels=["current-password"])
    context_action("username-field", "paste")
    # Text in clipboard should not have updated to random_other_text
    login_fill.element_attribute_contains("username-field", "value", random_text)

    # Delete all text
    login_fill.triple_click("username-field")
    login_fill.get_element("username-field").send_keys(Keys.BACK_SPACE)
    login_fill.element_attribute_contains(
        "username-field",
        attr_name="value",
        attr_value="",
    )


def test_text_area_copy_paste(driver: Firefox):
    # Initialize objects
    text_area_fill = TextAreaFormAutofill(driver)
    text_area_fill.open()
    util = Utilities()
    context_menu = ContextMenu(driver)

    # Send the text
    random_text = util.generate_random_text("sentence")
    text_area_fill.fill("street-address-textarea", random_text, press_enter=False)
    logging.info(f"Sent the text {random_text} to the textarea.")

    # Copy the text
    text_area_fill.triple_click("street-address-textarea")
    text_area_fill.context_click("street-address-textarea")
    context_menu.click_and_hide_menu("context-menu-copy")

    # Delete all the text and paste
    text_area_fill.get_element("street-address-textarea").send_keys(Keys.BACK_SPACE)
    text_area_fill.element_attribute_contains("street-address-textarea", "value", "")

    text_area_fill.context_click("street-address-textarea")
    context_menu.click_and_hide_menu("context-menu-paste")
    text_area_fill.element_attribute_contains(
        "street-address-textarea", "value", random_text
    )


def test_search_field_copy_paste(driver: Firefox):
    context_menu = ContextMenu(driver)
    google_search = GoogleSearch(driver)
    google_search.open()
    util = Utilities()

    # Send the text
    random_text = util.generate_random_text("sentence")
    google_search.fill("search-bar-textarea", random_text, press_enter=False)
    logging.info(f"Sent the text {random_text} to the search bar.")

    # Triple click the text to select all
    google_search.click_on("search-bar-textarea")
    google_search.triple_click("search-bar-textarea")

    # Context click
    google_search.context_click("search-bar-textarea")
    context_menu.click_and_hide_menu("context-menu-copy")

    # Delete the current text
    google_search.get_element("search-bar-textarea").send_keys(Keys.BACK_SPACE)
    google_search.element_attribute_contains("search-bar-textarea", "value", "")

    # Context click and paste the text back
    google_search.context_click("search-bar-textarea")
    context_menu.click_and_hide_menu("context-menu-paste")
    google_search.element_attribute_contains(
        "search-bar-textarea", "value", random_text
    )
