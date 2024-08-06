from time import sleep

import pytest
from pynput.keyboard import Controller, Key
from selenium.webdriver import Firefox

from modules.page_object import AboutPrefs
from modules.util import BrowserActions

COOKIE_SITE = "google.com"


@pytest.mark.headed
def test_manage_cookie_data(driver: Firefox):
    """
    C143633 - Cookies and Site Data can be managed
    via the "Managed Cookies and Site Data" pane
    """
    # Instantiate objects
    about_prefs = AboutPrefs(driver, category="privacy")
    ba = BrowserActions(driver)
    keyboard = Controller()

    def open_manage_cookies_data_dialog():
        about_prefs.open()
        manage_data_popup = about_prefs.press_button_get_popup_dialog_iframe(
            "Manage Data…"
        )
        ba.switch_to_iframe_context(manage_data_popup)

    # Visit some sites to get a few cookies added to saved data
    driver.get("https://www.google.com")
    driver.get("https://www.jetbrains.com")
    driver.get("https://www.wikipedia.com")

    # Navigate to the manage data dialog of about:preferences#privacy
    open_manage_cookies_data_dialog()

    # Click on one of the items from the list.
    cookie_item = about_prefs.get_manage_data_site_element(COOKIE_SITE)
    cookie_item.click()

    # The clicked on site in the list is highlighted
    selected = cookie_item.get_attribute("selected")
    assert selected == "true"

    # Click the "Remove Selected" button.
    about_prefs.get_element("remove-selected-button").click()

    # The selected item is removed from the list.
    about_prefs.element_does_not_exist("manage-cookies-site", labels=[COOKIE_SITE])

    # Click on the "Remove All" button and wait for changes to take.
    about_prefs.get_element("remove-all-button").click()
    sleep(1)

    # All the sites are removed from the list.
    # NOTE: There seems to be an empty placeholder element, thus 1 item is always there.
    cookie_list = about_prefs.get_elements("cookies-manage-data-sitelist")
    assert len(cookie_list) == 1

    # Click on "Save Changes" button and wait for changes to take.
    about_prefs.get_element("manage-data-save-changes-button").click()
    sleep(1)

    # Using pynput, navigate to the "Remove" button of the acceptance dialog/alert,
    # then send the Enter key and wait for changes to take
    keyboard.press(Key.tab)
    keyboard.release(Key.tab)
    sleep(0.5)
    keyboard.press(Key.tab)
    keyboard.release(Key.tab)
    sleep(0.5)
    keyboard.press(Key.enter)
    keyboard.release(Key.enter)
    sleep(1)

    # Navigate back to the manage data dialog of about:preferences#privacy
    open_manage_cookies_data_dialog()

    # All the cookies and site data are deleted.
    cookie_list_post_remove = about_prefs.get_elements("cookies-manage-data-sitelist")
    assert len(cookie_list_post_remove) == 1  # NOTE: always an empty item here
