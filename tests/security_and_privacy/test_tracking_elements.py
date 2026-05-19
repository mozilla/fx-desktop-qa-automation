import pytest
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
)
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from modules.browser_object import TrustPanel
from modules.page_object import AboutPrefs, GenericPage


@pytest.fixture
def test_case():
    return "446325"


def status_checker(span_id, expected):
    return (
        lambda d: (
            d.find_element(By.ID, span_id).get_attribute("textContent") or ""
        ).strip()
        == expected
    )


TRACKER_URL = "https://www.itisatrap.org/firefox/its-a-tracker.html"


def test_tracking_elements(driver: Firefox, trust_panel: TrustPanel):
    """
    C446325: Verify tracking elements are not blocked in normal browsing session
    """
    about_prefs = AboutPrefs(driver, category="privacy")

    # Make sure that the "Standard" option is selected from the ETP section in about:preferences#privacy
    about_prefs.open()
    about_prefs.click_on("standard-radio")

    # open the trackers page and save the current state of the page before changes
    GenericPage(driver, url=TRACKER_URL).open()
    old_body = driver.find_element(By.TAG_NAME, "body")

    # click on the shield icon
    trust_panel.open_panel()
    trust_panel.wait_for_trackers()

    # turn of the enhanced tracking protection toggle
    trust_panel.trustpanel_toggle_on_off()

    # wait until the page refreshes
    WebDriverWait(driver, 10).until(EC.staleness_of(old_body))

    # Wait for fresh DOM to have correct values (re-fetches each poll)
    wait = WebDriverWait(
        driver,
        10,
        ignored_exceptions=(StaleElementReferenceException, NoSuchElementException),
    )

    wait.until(status_checker("blacklisted-loaded", "incorrectly loaded"))
    wait.until(status_checker("whitelisted-loaded", "correctly loaded"))
    wait.until(status_checker("dnt-off", "incorrectly missing"))
