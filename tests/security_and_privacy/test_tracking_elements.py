import time

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from modules.browser_object import Navigation, TrustPanel
from modules.page_object import AboutPrefs, GenericPage


@pytest.fixture
def test_case():
    return "446325"


VISIT_URL = "about:preferences#privacy"
TRACKER_URL = "https://www.itisatrap.org/firefox/its-a-tracker.html"


def test_tracking_elements(
    driver: Firefox, trust_panel: TrustPanel, about_prefs_privacy: AboutPrefs
):
    pgg = GenericPage(driver, url=TRACKER_URL)
    about_prefs = AboutPrefs(driver, category="privacy")

    # Make sure that the "Standard" option is selected from the ETP section in about:preferences#privacy
    about_prefs.open()
    about_prefs.click_on("standard-radio")

    # wait for the shield icon
    pgg.open()
    trust_panel.open_panel()
    trust_panel.wait_for_trackers()

    trust_panel.click_tracking_protection_toggle()
    pg_body = pgg.get_element("page-body")
    # result1 = driver.find_element(By.XPATH, '//*[@id="blacklisted-loaded"]')
    # result2 = driver.find_element(By.XPATH, '//*[@id="whitelisted-loaded"]')
    # result3 = driver.find_element(By.XPATH, '//*[@id="dnt-off"]')

    # print(f"-------------------result1----->{result1.text}")
    # print(f"-------------------result2----->{result2.text}")
    # print(f"-------------------result3----->{result3.text}")
    # assert result1.text == "incorrectly loaded", f"Expected incorrectly loaded but got: {result1.text}"
    # assert result2.text == "correctly loaded", f"Expected correctly loaded but got: {result2.text}"
    # assert result3.text == "incorrectly missing", f"Expected incorrectly loaded but got: {result3.text}"
