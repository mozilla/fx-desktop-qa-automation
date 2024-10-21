import pytest
import time
from pynput.keyboard import Controller, Key
from selenium.webdriver import Firefox

from modules.page_object import AboutLogins, GenericPage
from modules.browser_object import AutofillPopup


@pytest.fixture()
def test_case():
    return "2240907"


@pytest.fixture()
def set_prefs():
    """Set prefs"""
    return [("signon.rememberSignons", True)]


@pytest.fixture()
def temp_selectors():
    return {
        "username-field": {
            "selectorData": "email", 
            "strategy": "id", 
            "groups": []
        },
        "password-field":{
            "selectorData": "pass",
            "strategy": "id",
            "groups": []
        }
    }

FACEBOOK_URL = "https://www.facebook.com/"


@pytest.mark.headed
def test_multiple_saved_logins(driver: Firefox, temp_selectors):
    """
    C2240907 - Verify that autocomplete dropdown is toggled for focused login fields on page load
    """
    # Instantiate objects
    about_logins = AboutLogins(driver)
    keyboard = Controller()

    # Save 3 sets of credentials for facebook
    about_logins.open()
    about_logins.click_add_login_button()
    about_logins.create_new_login(
        {
            "origin": "https://www.facebook.com",
            "username": "username1",
            "password": "password1",
        }
    )
    time.sleep(0.1)
    about_logins.click_add_login_button()
    about_logins.create_new_login(
        {
            "origin": "https://www.facebook.com",
            "username": "username2",
            "password": "password2",
        }
    )
    time.sleep(0.1)
    about_logins.click_add_login_button()
    about_logins.create_new_login(
        {
            "origin": "https://www.facebook.com",
            "username": "username3",
            "password": "password3",
        }
    )

    # Open Facebook.com
    web_page = GenericPage(driver, url=FACEBOOK_URL).open()
    web_page.elements |= temp_selectors
    autofill_popup = AutofillPopup(driver)

    # Verify that all 3 credentials and "Manage Passwords" footer are in the pop-up
    autofill_popup.verify_autofill_displayed()
    for i in range(1, 4):
        credential = autofill_popup.get_nth_element(str(i))
        assert autofill_popup.get_primary_value(credential) == f"username{i}"
    footer = autofill_popup.get_nth_element("4")
    assert autofill_popup.get_primary_value(footer) == "Manage Passwords"

    # Check that "about:logins" is opened when clicking "Manage Password" in the Context Menu
    web_page.context_click("username-field")
    keyboard.press(Key.down)
    keyboard.press(Key.down)
    keyboard.press(Key.enter)
    web_page.switch_to_new_tab()
    web_page.url_contains("about:logins")
    
    def use_credential_n(n: int):
        """
        Uses the n-th saved password within the context menu
        """
        web_page.context_click("username-field")
        keyboard.press(Key.down)
        keyboard.press(Key.enter)
        time.sleep(0.1)
        for _ in range(n-1):
            keyboard.press(Key.down)
        keyboard.press(Key.enter)

    # Verify the all 3 credientials are correct when autofilling
    driver.switch_to.window(driver.window_handles[0])
    for i in range(1, 4):
        use_credential_n(i)
        web_page.element_attribute_contains("username-field", "value", f"username{i}")
        web_page.element_attribute_contains("password-field", "value", f"password{i}")
        