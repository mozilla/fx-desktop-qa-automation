import pytest
from selenium.webdriver import Firefox

from modules.browser_object_tabbar import TabBar
from modules.page_object_about_pages import AboutLogins
from modules.page_object_autofill import LoginAutofill
from modules.page_object_generics import GenericPage


BSKY_URL = "https://bsky.app/"
USERNAME = "username1"
PASSWORD = "password1"
USERNAME2 = "username2"
PASSWORD2 = "password2"


@pytest.fixture()
def test_case():
    return "2240907"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [("signon.rememberSignons", True)]


def test_autocomplete_dropdown_is_toggled_for_focused_login_fields_on_page_load(
    driver: Firefox,
):
    """
    C2240907 - Verify that autocomplete dropdown is toggled for focused login fields on page load
    """
    # Instantiate objects
    tabs = TabBar(driver)
    about_logins = AboutLogins(driver)
    login_autofill = LoginAutofill(driver)
    generic_page = GenericPage(driver)

    # Go to a site that have login field focus on page load
    GenericPage(driver, url=BSKY_URL).open()
    tabs.new_tab_by_button()
    tabs.switch_to_new_tab()

    # Save 2 set of credentials for the visited site
    about_logins.open()
    about_logins.click_add_login_button()
    about_logins.create_new_login(
        {
            "origin": BSKY_URL,
            "username": USERNAME,
            "password": PASSWORD,
        }
    )
    about_logins.click_add_login_button()
    about_logins.create_new_login(
        {
            "origin": BSKY_URL,
            "username": USERNAME2,
            "password": PASSWORD2,
        }
    )

    # Autocomplete dropdown is toggled for focused login fields on page load
    tabs.click_tab_by_index(1)
    driver.switch_to.window(driver.window_handles[0])
    generic_page.get_element("bsky-signin-button").click()
    with driver.context(driver.CONTEXT_CHROME):
        username_element = login_autofill.get_element("bsky-credentials")
        assert username_element.get_attribute("ac-value") == USERNAME
