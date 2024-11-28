from modules.page_object import AboutLogins
from modules.util import BrowserActions


def test_about_logins_search_functionality(driver_and_saved_logins):
    """Basic test of about:logins search, case number tbd"""
    (driver, usernames, logins) = driver_and_saved_logins
    about_logins = AboutLogins(driver).open()
    ba = BrowserActions(driver)
    ba.clear_and_fill(about_logins.get_element("login-filter-input"), usernames[-1])
