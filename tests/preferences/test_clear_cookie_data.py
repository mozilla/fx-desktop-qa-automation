import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutPrefs


@pytest.fixture()
def test_case():
    return "143627"


@pytest.fixture()
def about_prefs_category():
    return "privacy"


WEBSITE_ADDRESS = "https://www.wikipedia.com"


def test_clear_cookie_data(driver: Firefox, about_prefs: AboutPrefs):
    """
    C143627: Cookies and site data can be cleared via the "Clear Data" panel
    """
    # Visit a site to get a cookie added to saved data
    driver.get(WEBSITE_ADDRESS)

    # Open dialog and read current value (must be > 0)
    cookie_value = about_prefs.open_clear_cookie_site_and_get_data()
    assert cookie_value > 0, f"Expected cookie/site data > 0, got {cookie_value}"

    # Clear cookies and site data: open the dialog again, wait for iframe, click clear
    about_prefs.open_clear_cookie_site_and_clear_data()

    # Wait until the dialog reports 0 (reopen/poll via helper)
    cookie_value = about_prefs.open_clear_cookie_site_and_get_data()
    assert cookie_value == 0, f"Expected 0 after clearing, got {cookie_value}"
