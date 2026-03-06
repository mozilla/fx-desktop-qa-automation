import pytest
from selenium.webdriver import Firefox

from modules.browser_object_tabbar import TabBar
from modules.page_object_about_pages import AboutLogins

TEST_PAGE_URL = "mozilla.github.io"
USERNAME = "username1"
PASSWORD = "password1"


@pytest.fixture()
def test_case():
    return "2241463"


def test_about_logins_menu_options(driver: Firefox):
    """
    C2241463 - Verify that the options in the Settings menu responds correctly upon selection
    """

    # Instantiate object
    about_logins = AboutLogins(driver)
    tabs = TabBar(driver)

    # Open about:logins and have at least one login is saved
    about_logins.open()
    about_logins.add_login(TEST_PAGE_URL, USERNAME, PASSWORD)

    # Click on each option in the Settings menu and check that all options redirects to the corresponding path
    # Click on "Import from another browser" button
    about_logins.click_menu_option("menuitem-import-from-another-browser")
    tabs.switch_to_new_tab()
    about_logins.url_contains("about:preferences#general")

    # Close tab and go back to about:logins page
    tabs.close_current_tab_and_switch_back()

    # Click on "Import from a file" button
    about_logins.click_menu_option("menuitem-import-from-file")
    about_logins.confirm_and_click_cancel_import_dialog()

    # Click on "Export passwords" button
    about_logins.click_menu_option("menuitem-export-passwords")
    about_logins.element_visible("dismiss-export-button")
    about_logins.click_on("dismiss-export-button")

    # Click on "Remove all passwords" button
    about_logins.click_menu_option("menuitem-remove-all-passwords")
    about_logins.element_visible("dismiss-delete-passwords-button")
    about_logins.click_on("dismiss-delete-passwords-button")

    # Click on "Preferences"
    about_logins.click_menu_option("menuitem-preferences")
    tabs.switch_to_new_tab()
    about_logins.url_contains("about:preferences#privacy-logins")

    # Close tab and go back to about:logins page
    tabs.close_current_tab_and_switch_back()

    # Click on "Help"
    about_logins.click_menu_option("menuitem-help")
    tabs.switch_to_new_tab()
    about_logins.url_contains("support.mozilla.org")
