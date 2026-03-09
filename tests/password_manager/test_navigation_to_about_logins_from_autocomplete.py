import pytest
from selenium.webdriver import Firefox

from modules.browser_object_autofill_popup import AutofillPopup
from modules.browser_object_tabbar import TabBar
from modules.page_object_about_pages import AboutLogins
from modules.page_object_autofill import LoginAutofill

TEST_PAGE_URL = "https://mozilla.github.io/"
USERNAME = "username1"
PASSWORD = "password1"


@pytest.fixture()
def test_case():
    return "2241086"


@pytest.fixture()
def add_to_prefs_list():
    return [("signon.rememberSignons", True)]


def test_navigation_to_about_logins_from_autocomplete(driver: Firefox):
    """
    C2241086 - Verify the navigation to about:logins from a password form autocomplete
    """

    # Instantiate objects
    login = LoginAutofill(driver)
    about_logins = AboutLogins(driver)
    autofill_popup_panel = AutofillPopup(driver)
    tabs = TabBar(driver)

    # Have at least one saved login
    about_logins.open()
    about_logins.add_login(TEST_PAGE_URL, USERNAME, PASSWORD)

    # Have a login page of a website opened
    login.open()

    # Click the "Username" field and click the "Manage passwords" button from the menu that appears
    login.click_on("username-field")
    autofill_popup_panel.click_manage_passwords()

    # The "about:logins" page is successfully opened in a new tab
    tabs.switch_to_new_tab()
    login.url_contains("about:logins")
