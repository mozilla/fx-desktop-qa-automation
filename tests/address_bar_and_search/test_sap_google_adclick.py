from time import sleep

import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.page_object_about_pages import AboutConfig, AboutTelemetry
from modules.util import Utilities

# Constants
SEARCH_TERM = "iphone"
SLEEP_AFTER_CLICK = 2
SLEEP_BEFORE_VERIFICATION = 2


@pytest.fixture()
def test_case():
    return "1365108"


@pytest.mark.unstable(reason="Google re-captcha")
def test_sap_google_adclick(driver: Firefox):
    """
    C1365108 - Verify Google ad click from URL bar is recorded in telemetry (US region).
    """
    nav = Navigation(driver)
    about_config = AboutConfig(driver)
    utils = Utilities()

    # Disable cookie banner
    about_config.change_config_value("cookiebanners.service.mode", 1)

    # Search and click on ad result
    nav.search(SEARCH_TERM)
    nav.get_element("search-result").click()
    sleep(SLEEP_AFTER_CLICK)

    # Open telemetry and raw data
    telemetry = AboutTelemetry(driver).open()
    sleep(SLEEP_BEFORE_VERIFICATION)
    telemetry.get_element("category-raw").click()
    telemetry.switch_to_new_tab()
    telemetry.get_element("rawdata-tab").click()

    # Validate telemetry ping
    json_data = utils.decode_url(driver)
    assert utils.assert_json_value(
        json_data,
        '$..keyedScalars.["browser.search.adclicks.urlbar"].["google:tagged"]',
        1,
    )
