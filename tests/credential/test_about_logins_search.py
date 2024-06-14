from typing import List, Tuple

import pytest
from selenium.webdriver import Firefox

from modules.page_object import AboutLogins
from modules.util import BrowserActions


@pytest.mark.unstable
def test_about_logins_search_functionality(
    driver_and_saved_usernames: Tuple[Firefox, List[str]],
):
    """Basic test of about:logins search, case number tbd"""
    (driver, usernames) = driver_and_saved_usernames
    about_logins = AboutLogins(driver).open()
    ba = BrowserActions(driver)
    ba.clear_and_fill(about_logins.get_element("login-filter-input"), usernames[-1])
