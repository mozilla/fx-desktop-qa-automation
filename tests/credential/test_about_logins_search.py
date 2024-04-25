from typing import List, Tuple

from selenium.webdriver import Firefox

from modules.page_object import AboutLogins
from modules.util import BrowserActions


def test_about_logins_search_functionality(
    driver_and_saved_usernames: Tuple[Firefox, List[str]],
):
    (driver, usernames) = driver_and_saved_usernames
    about_logins = AboutLogins(driver).open()
    ba = BrowserActions(driver)
    ba.clear_and_fill(about_logins.get_element("login-filter-input"), usernames[-1])
