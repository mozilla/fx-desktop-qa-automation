import logging

import pytest
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Firefox

from modules.browser_object import AutofillPopup
from modules.page_object import AboutLogins, GenericPage

SAUCEDEMO_URL = "https://www.saucedemo.com/"
USERNAME = "username1"
PASSWORD = "password1"
USERNAME2 = "username2"
PASSWORD2 = "password2"
USERNAME3 = "username3"
PASSWORD3 = "password3"


@pytest.fixture()
def test_case():
    return "2240897"


@pytest.fixture()
def add_to_prefs_list():
    """Add to list of prefs to set"""
    return [("signon.rememberSignons", True)]


@pytest.fixture()
def temp_selectors():
    return {
        "username-field": {"selectorData": "user-name", "strategy": "id", "groups": []},
        "password-field": {"selectorData": "password", "strategy": "id", "groups": []},
    }


def open_manage_passwords_via_context_menu(web_page, retries: int = 3):
    """
    Right-click the username field and select "Manage Passwords" from the
    context menu, retrying if the expected new tab doesn't open.
    """
    for attempt in range(retries):
        web_page.context_click("username-field")
        web_page.gui_sequence("down", "down", "enter")
        try:
            web_page.wait_for_num_tabs(2)
            return
        except TimeoutException:
            web_page.gui.press("escape")
            if attempt == retries - 1:
                raise


def use_credential_n(web_page, n: int, retries: int = 3):
    """
    Selects the n-th saved credential via the context menu's Fill Login
    submenu, retrying if the fields weren't filled as expected.
    """
    sequence = ["down", "enter"]
    sequence.extend(["down"] * (n - 1))
    sequence.append("enter")

    for attempt in range(retries):
        web_page.context_click("username-field")
        web_page.gui_sequence(*sequence)
        try:
            web_page.element_attribute_contains(
                "username-field", "value", f"username{n}"
            )
            web_page.element_attribute_contains(
                "password-field", "value", f"password{n}"
            )
            return
        except TimeoutException:
            web_page.gui.press("escape")
            if attempt == retries - 1:
                raise


@pytest.mark.headed
def test_multiple_saved_logins(driver: Firefox, temp_selectors):
    """
    C2240897 - Verify that the fill functionality works when there are multiple saved credentials
    """
    # Instantiate objects
    about_logins = AboutLogins(driver)
    autofill_popup = AutofillPopup(driver)

    # Save 3 sets of credentials for Saucedemo
    about_logins.open()
    about_logins.add_login_and_wait(SAUCEDEMO_URL, USERNAME, PASSWORD)
    about_logins.add_login_and_wait(SAUCEDEMO_URL, USERNAME2, PASSWORD2)
    about_logins.add_login_and_wait(SAUCEDEMO_URL, USERNAME3, PASSWORD3)

    # Open saucedemo.com
    web_page = GenericPage(driver, url=SAUCEDEMO_URL).open()
    web_page.elements |= temp_selectors

    # Verify that all 3 credentials and "Manage Passwords" footer are in the pop-up
    web_page.click_on("username-field")
    autofill_popup.ensure_autofill_dropdown_visible()
    for i in range(1, 4):
        credential = autofill_popup.get_nth_element(str(i))
        assert autofill_popup.get_primary_value(credential) == f"username{i}"
    footer = autofill_popup.get_nth_element("4")
    assert autofill_popup.get_primary_value(footer) == "Manage Passwords"

    # Check that "about:logins" is opened when clicking "Manage Password" in the Context Menu
    open_manage_passwords_via_context_menu(web_page)
    web_page.switch_to_new_tab()
    web_page.url_contains("about:logins")

    # Verify all 3 credentials are correct when autofilling
    driver.switch_to.window(driver.window_handles[0])
    for i in range(1, 4):
        logging.warning(f"Attempting username{i}")
        use_credential_n(web_page, i)
