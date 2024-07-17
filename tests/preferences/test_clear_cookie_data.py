from selenium.webdriver import Firefox

from modules.page_object import AboutPrefs
from modules.util import BrowserActions


def test_clear_cookie_data(driver: Firefox):
    """
    C143627: Cookies and site data can be cleared via the "Clear Data" panel
    """
    # Instantiate objects
    about_prefs = AboutPrefs(driver, category="privacy")
    ba = BrowserActions(driver)

    def open_clear_cookies_data_dialog():
        about_prefs.open()
        clear_data_popup = about_prefs.press_button_get_popup_dialog_iframe(
            "Clear Data…"
        )
        ba.switch_to_iframe_context(clear_data_popup)

    # Visit a site to get a cookie added to saved data
    driver.get("https://www.mozilla.org")

    # Navigate to the clear data dialog of about:preferences#privacy
    open_clear_cookies_data_dialog()

    # Check for a non-zero value of the 'Cookies and site data' option
    cookie_value = about_prefs.get_clear_cookie_data_value()
    assert cookie_value != 0

    # Then clear the cookies and site data
    about_prefs.get_element("clear-data-accept-button").click()

    # Finally, check the value of the dialog option, it should be 0
    open_clear_cookies_data_dialog()
    cookie_value2 = about_prefs.get_clear_cookie_data_value()
    assert cookie_value2 == 0
