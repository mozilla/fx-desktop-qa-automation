import time

import pyautogui
import pytest
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
    about_logins.add_login(SAUCEDEMO_URL, USERNAME, PASSWORD)
    time.sleep(0.8)
    about_logins.add_login(SAUCEDEMO_URL, USERNAME2, PASSWORD2)
    time.sleep(0.8)
    about_logins.add_login(SAUCEDEMO_URL, USERNAME3, PASSWORD3)

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
    web_page.context_click("username-field")
    pyautogui.press("down", presses=2, interval=0.1)
    pyautogui.press("enter")
    web_page.wait_for_num_tabs(2)
    web_page.switch_to_new_tab()
    web_page.url_contains("about:logins")

    def use_credential_n(n: int):
        """
        Uses the n-th saved password within the context menu
        """
        web_page.context_click("username-field")
        pyautogui.press("down")
        pyautogui.press("enter")
        time.sleep(0.2)
        pyautogui.press("down", presses=n - 1, interval=0.1)
        pyautogui.press("enter")
        time.sleep(0.2)

    # Verify the all 3 credientials are correct when autofilling
    driver.switch_to.window(driver.window_handles[0])
    for i in range(1, 4):
        use_credential_n(i)
        web_page.element_attribute_contains("username-field", "value", f"username{i}")
        web_page.element_attribute_contains("password-field", "value", f"password{i}")
