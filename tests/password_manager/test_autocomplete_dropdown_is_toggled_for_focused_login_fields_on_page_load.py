from time import sleep

import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.browser_object_tabbar import TabBar
from modules.page_object_about_pages import AboutLogins
from modules.page_object_generics import GenericPage


@pytest.fixture()
def test_case():
    return "2240907"


@pytest.fixture()
def set_prefs():
    """Set prefs"""
    return [("signon.rememberSignons", True), ("signon.autofillForms", True), ("cookiebanners.service.mode", 1)]


FACEBOOK_URL = "https://www.facebook.com/"
QUORA_URL = "https://www.quora.com/"


def test_autocomplete_dropdown_is_toggled_for_focused_login_fields_on_page_load(driver: Firefox):
    """
    C2240907 - Verify that autocomplete dropdown is toggled for focused login fields on page load
    """
    tabs = TabBar(driver)
    about_logins = AboutLogins(driver)
    navigation = Navigation(driver)

    # Go to sites that have login field focus on page load
    GenericPage(driver, url=FACEBOOK_URL).open()
    tabs.new_tab_by_button()
    tabs.switch_to_new_tab()
    GenericPage(driver, url=QUORA_URL).open()

    # Save 2 set of credentials for each of the visited sites
    tabs.new_tab_by_button()
    tabs.switch_to_new_tab()
    about_logins.open()
    about_logins.click_add_login_button()
    about_logins.create_new_login(
        {
            "origin": "https://www.facebook.com/",
            "username": "username1",
            "password": "password1",
        }
    )
    about_logins.click_add_login_button()
    about_logins.create_new_login(
        {
            "origin": "https://www.quora.com/",
            "username": "username2",
            "password": "password2",
        }
    )

    tabs.click_tab_by_index(1)
    navigation.get_element("refresh-button").click()
    sleep(4)

    # tabs.click_tab_by_index(2)
    # with driver.context(driver.CONTEXT_CHROME):
        # navigation.get_element("refresh-button").click()
    # sleep(4)
