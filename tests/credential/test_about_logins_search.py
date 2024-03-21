from selenium.webdriver import Firefox
from modules.util import BrowserActions
from modules.page_object import AboutLogins
from typing import Tuple
from typing import List


def test_about_logins_search_functionality(
    driver_and_saved_usernames: Tuple[Firefox, List[str]],
):
    (driver, usernames) = driver_and_saved_usernames
    about_logins = AboutLogins(driver).open()
    ba = BrowserActions(driver)
    ba.clear_and_fill(about_logins.search_input(), usernames[-1])
