import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from modules.util import BrowserActions
from modules.shadow_dom import AboutLogins
from collections.abc import Iterable


def test_about_logins_search_functionality(
    driver_and_saved_usernames: Iterable[Firefox, Iterable[str]]
):
    (driver, usernames) = driver_and_saved_usernames
    about_logins = AboutLogins(driver)
    ba = BrowserActions(driver)
    driver.get("about:logins")
    ba.clear_and_fill(about_logins.search_input(), usernames[-1])
