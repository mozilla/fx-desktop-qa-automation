from time import sleep

import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.page_object_about_config import AboutConfig
from modules.page_object_about_telemetry import AboutTelemetry
from modules.util import Utilities


@pytest.mark.unstable
def test_sap_google_adclick(driver: Firefox):
    """
    C1365108, Test SAP Google adclick - URL bar - US
    """
    # instantiate objects
    nav = Navigation(driver).open()
    about_config = AboutConfig(driver)
    u = Utilities()

    # change pref value in order to not display accept cookies banner
    about_config.change_pref_value("cookiebanners.service.mode", 1)

    # search and click on an ad
    nav.search("iphone")
    nav.get_element("search-result").click()
    sleep(2)

    # Click on Raw JSON, switch tab and click on Raw Data
    about_telemetry = AboutTelemetry(driver).open()
    sleep(2)
    about_telemetry.get_element("category-raw").click()
    about_telemetry.switch_to_new_tab()
    about_telemetry.get_element("rawdata-tab").click()

    # Verify pings are recorded
    json_data = u.decode_url(driver)
    assert u.assert_json_value(
        json_data,
        '$..keyedScalars.["browser.search.adclicks.urlbar"].["google:tagged"]',
        1,
    )
