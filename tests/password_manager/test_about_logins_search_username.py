import pytest
from selenium.webdriver.common.keys import Keys

from modules.page_object import AboutLogins
from modules.util import BrowserActions


@pytest.fixture()
def test_case():
    return "2241116"


def test_about_logins_search_username(driver_and_saved_logins):
    """
    C2241116: Check that the search function filters passwords correctly using usernames
    """
    # Initializing objects
    (driver, usernames, logins) = driver_and_saved_logins
    about_logins = AboutLogins(driver)
    ba = BrowserActions(driver)

    # Open about:logins and search for a username with 2 results
    about_logins.open()
    ba.clear_and_fill(about_logins.get_element("login-filter-input"), usernames[-1])

    # Check that only the correct 2 results are shown
    results = about_logins.get_elements("login-list-item")
    results = [result for result in results if result.is_displayed()]
    assert len(results) == 2
    assert (
        about_logins.get_element("login-count").get_attribute("innerHTML")
        == "2 of 6 passwords"
    )
    for item in results:
        assert item.get_attribute("username") == usernames[-1]
        assert item.get_attribute("title") in ("bsky.app", "mozilla.social")

    # Delete the entered username and see if all 6 results are shown
    about_logins.perform_key_combo(Keys.BACKSPACE * 20)
    results_after = about_logins.get_elements("login-list-item")
    results_after = [result for result in results_after if result.is_displayed()]
    assert (
        about_logins.get_element("login-count").get_attribute("innerHTML")
        == "6 passwords"
    )
    actual_logins = {}
    for e in results_after:
        actual_logins[e.get_attribute("username") + "@" + e.get_attribute("title")] = ""
    about_logins.check_logins_present(actual_logins, logins)
