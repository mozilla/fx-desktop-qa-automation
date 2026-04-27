import pytest
from selenium.webdriver import Firefox

from modules.page_object_about_pages import AboutLogins

TEST_PAGE_URL = "mozilla.github.io"
USERNAME = "username1"
PASSWORD = "password1"
TEST_PAGE_URL2 = "mozilla.org"
USERNAME2 = "username2"
PASSWORD2 = "password2"
TEST_PAGE_URL3 = "reddit.com"
USERNAME3 = "username3"
PASSWORD3 = "password3"


@pytest.fixture()
def test_case():
    return "2241118"


def test_about_logins_search_passwords(driver: Firefox):
    """
    C2241118 - Verify that searching by password in the Search Bar returns correct results
    """

    # Instantiate object
    about_logins = AboutLogins(driver)

    # Open about:logins and have at least one login is saved
    about_logins.open()
    about_logins.add_login(TEST_PAGE_URL, USERNAME, PASSWORD)
    about_logins.add_login(TEST_PAGE_URL, USERNAME2, PASSWORD2)
    about_logins.add_login(TEST_PAGE_URL, USERNAME3, PASSWORD3)

    # Click on the Search bar and search using a saved password
    password_search = about_logins.get_element("login-filter-input")
    password_search.send_keys(PASSWORD)

    # A "[x] of [x] passwords" message displayed next to the "Sort by" section
    results = about_logins.get_elements("login-list-item")
    results = [result for result in results if result.is_displayed()]
    assert (
        about_logins.get_element("login-count").get_attribute("innerHTML")
        == "1 of 3 passwords"
    )

    # All saved logins containing the searched password are correctly displayed
    assert results[0].get_attribute("title") == TEST_PAGE_URL
