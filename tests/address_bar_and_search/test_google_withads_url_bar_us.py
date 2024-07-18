from time import sleep

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation
from modules.page_object import AboutTelemetry
from modules.util import Utilities


@pytest.fixture()
def add_prefs():
    return [("cookiebanners.service.mode", 1)]


def test_google_withads_url_bar_us(driver: Firefox):
    """
    C1365070, verify that Google withads URL bar - US is recorder into telemetry
    """

    # instantiate objects
    nav = Navigation(driver).open()
    util = Utilities()

    nav.search("iphone")
    sleep(5)
    about_telemetry = AboutTelemetry(driver).open()
    sleep(5)

    # Click on Raw JSON, switch tab and click on Raw Data
    about_telemetry.get_element("category-raw").click()
    about_telemetry.switch_to_new_tab()
    about_telemetry.get_element("rawdata-tab").click()

    # Verify the following ping is recorded: ""browser.search.withads.urlbar": { "google:tagged": 1}".
    with driver.context(driver.CONTEXT_CONTENT):
        json_data = util.decode_url(driver)
        assert util.assert_json_value(
            json_data, '$..["browser.search.withads.urlbar"].["google:tagged"]', 1
        )
