import sys
from os import environ
from time import sleep

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation
from modules.page_object import AboutTelemetry
from modules.util import Utilities

# Constants
SEARCH_TERM = "festival"
SEARCH_PROVIDER_PATH = '$..SEARCH_COUNTS.["google-b-1-d.urlbar"].sum'
SEARCH_TAG_PATH = '$..["browser.search.content.urlbar"].["google:tagged:firefox-b-1-d"]'
WAIT_AFTER_SEARCH = 5
WAIT_TELEMETRY_LOAD = 2

MAC_GHA = environ.get("GITHUB_ACTIONS") == "true" and sys.platform.startswith("darwin")


@pytest.fixture()
def test_case():
    return "3029528"


@pytest.mark.skipif(MAC_GHA, reason="Test unstable in macOS GitHub Actions")
def test_google_search_counts_us(driver: Firefox):
    """
    C1365026 - Verify Google search counts in telemetry from the URL bar (US region).
    Retries up to 5 times if telemetry is missing or blocked by CAPTCHA.
    """
    max_attempts = 5
    for attempt in range(1, max_attempts + 1):
        nav = Navigation(driver)
        nav.search(SEARCH_TERM)
        sleep(WAIT_AFTER_SEARCH)

        utils = Utilities()

        telemetry = AboutTelemetry(driver).open()
        sleep(WAIT_TELEMETRY_LOAD)
        telemetry.get_element("category-raw").click()
        telemetry.switch_to_new_tab()
        telemetry.get_element("rawdata-tab").click()

        json_data = utils.decode_url(driver)

        if "recaptcha" in driver.page_source.lower():
            if attempt < max_attempts:
                driver.delete_all_cookies()
                driver.get("about:newtab")
                sleep(2)
                continue
            else:
                pytest.fail("CAPTCHA triggered repeatedly. Giving up after 5 attempts.")

        provider_ok = utils.assert_json_value(json_data, SEARCH_PROVIDER_PATH, 1)
        tag_ok = utils.assert_json_value(json_data, SEARCH_TAG_PATH, 1)

        if provider_ok and tag_ok:
            return  # Success

        if attempt < max_attempts:
            sleep(2)
            driver.get("about:newtab")
        else:
            pytest.fail(
                f"Telemetry paths not found after {max_attempts} attempts:\n"
                f"{SEARCH_PROVIDER_PATH} and/or {SEARCH_TAG_PATH}"
            )
