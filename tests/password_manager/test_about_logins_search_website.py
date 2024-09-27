import pytest

from selenium.webdriver.common.keys import Keys
from modules.page_object import AboutLogins
from modules.util import BrowserActions


@pytest.fixture()
def test_case():
    return "2241117"


def test_about_logins_search_website(origins, driver_and_saved_logins):
    """
    C2241117: Check that the search function filters passwords correctly using websites
    """
    # Initializing objects
    (driver, usernames, logins) = driver_and_saved_logins
    about_logins = AboutLogins(driver).open()
    ba = BrowserActions(driver)

    # Search for a website
    ba.clear_and_fill(about_logins.get_element("login-filter-input"), origins[1])

    # Check that only the correct 1 result is shown
    results = about_logins.get_elements("login-list-item")
    results = [result for result in results if result.is_displayed()]
    assert about_logins.get_element("login-count").get_attribute("innerHTML") == "1 of 6 passwords"
    assert results[0].get_attribute("title") == origins[1]

    # Delete the entered username and see if all 6 results are shown
    about_logins.perform_key_combo(Keys.BACKSPACE * 20)
    results_after = about_logins.get_elements("login-list-item")
    results_after = [result for result in results_after if result.is_displayed()]
    actual_logins = {}
    for e in results_after:
        actual_logins[e.get_attribute("username") + "@" + e.get_attribute("title")] = ""
    about_logins.check_logins_present(actual_logins, logins)
    assert about_logins.get_element("login-count").get_attribute("innerHTML") == "6 passwords"
