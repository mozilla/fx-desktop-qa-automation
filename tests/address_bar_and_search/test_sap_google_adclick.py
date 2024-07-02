import time

import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation

from modules.page_object_about_telemetry import AboutTelemetry
from modules.util import Utilities


@pytest.fixture()
def add_prefs():
    return [
        ("browser.search.region", "US"),
    ]


def test_sap_google_adclick(driver: Firefox):
    """
    C1365108, Test SAP Google adclick - URL bar - US
    """
    # instantiate objects
    nav = Navigation(driver).open()
    nav.search("iphone")
    time.sleep(2)
    u = Utilities()

    # click on any ad
    nav.get_element("accept-cookies").click()
    nav.get_element("search-result").click()
    time.sleep(2)

    # Click on Raw JSON, switch tab and click on Raw Data
    about_telemetry = AboutTelemetry(driver).open()
    about_telemetry.get_element("category-raw").click()
    about_telemetry.switch_tab()
    about_telemetry.get_element("rawdata-tab").click()

    # Verify pings are recorded
    json_data = u.decode_url(driver)
    assert u.assert_json_value(
        json_data, '$..keyedScalars.["browser.search.adclicks.urlbar"].["google:tagged"]', 1
    )