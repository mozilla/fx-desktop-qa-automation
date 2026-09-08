import pytest
from selenium.webdriver import Firefox, Keys

from modules.browser_object_autofill_popup import AutofillPopup
from modules.browser_object_tabbar import TabBar
from modules.page_object_about_pages import AboutLogins
from modules.page_object_generics import GenericPage

TEST_PAGE = "https://www.facebook.com/"
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
    autofill_popup = AutofillPopup(driver)

    # Go to a site that have login field focus on page load
    web_page = GenericPage(driver, url=TEST_PAGE).open_facebook_login()

    tabs.new_tab_by_button()
    tabs.switch_to_new_tab()

    # Save 2 set of credentials for the visited site
    about_logins.open()
    about_logins.add_login(TEST_PAGE, USERNAME, PASSWORD)
    about_logins.add_login(TEST_PAGE, USERNAME2, PASSWORD2)

    # Autocomplete dropdown is toggled for focused login fields on page load
    tabs.click_tab_by_index(1)
    driver.switch_to.window(driver.window_handles[0])

    # Click triggers focus; arrow key reliably triggers the dropdown
    username_field = web_page.get_element("facebook-username-field")
    web_page.click_on("facebook-username-field")
    username_field.send_keys(Keys.ARROW_DOWN)

    # The saved credential row is shown in the auto-toggled autocomplete dropdown.
    # Firefox 154 removed the richlistitem ac-value attribute, so match the row by
    # its label (read from the autocomplete-row-item shadow DOM) instead.
    autofill_popup.ensure_autofill_dropdown_visible()
    autofill_popup.verify_autocomplete_option(USERNAME)
