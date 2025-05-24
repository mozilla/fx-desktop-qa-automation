import sys
from os import environ
from time import sleep

import pytest

from modules.browser_object import Navigation
from modules.page_object import AboutTelemetry
from modules.util import Utilities

MAC_GHA = environ.get("GITHUB_ACTIONS") == "true" and sys.platform.startswith("darwin")


@pytest.fixture()
def test_case():
    return "3029577"


@pytest.fixture()
def add_to_prefs_list():
    return [("cookiebanners.service.mode", 1)]


@pytest.mark.unstable(reason="Google re-captcha")
@pytest.mark.skipif(MAC_GHA, reason="Test unstable in MacOS Github Actions")
def test_google_withads_url_bar_us(driver):
    """
    C1365070 - Retry up to 5 times if Google CAPTCHA blocks telemetry path.
    """
    max_attempts = 5
    search_term = "iphone"
    path = '$..["browser.search.withads.urlbar"].["google:tagged"]'
    util = Utilities()

    for attempt in range(1, max_attempts + 1):
        nav = Navigation(driver)
        nav.search(search_term)
        sleep(5)

        if "recaptcha" in driver.page_source.lower():
            if attempt < max_attempts:
                driver.delete_all_cookies()
                driver.get("about:newtab")
                sleep(2)
                continue
            else:
                pytest.fail("CAPTCHA triggered repeatedly. Giving up after 5 attempts.")

        about_telemetry = AboutTelemetry(driver).open()
        sleep(5)
        about_telemetry.get_element("category-raw").click()
        about_telemetry.switch_to_new_tab()
        about_telemetry.get_element("rawdata-tab").click()

        json_data = util.decode_url(driver)
        if util.assert_json_value(json_data, path, 1):
            return

        if attempt < max_attempts:
            sleep(2)
            driver.get("about:newtab")
        else:
            pytest.fail(
                f"Telemetry path {path} not found after {max_attempts} attempts."
            )
