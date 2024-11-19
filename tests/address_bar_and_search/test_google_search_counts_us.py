import sys
from os import environ
from time import sleep

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation
from modules.page_object import AboutTelemetry
from modules.util import Utilities


@pytest.fixture()
def test_case():
    return "1365026"


MAC_GHA = environ.get("GITHUB_ACTIONS") == "true" and sys.platform.startswith("darwin")


@pytest.mark.skipif(MAC_GHA, reason="Test unstable in MacOS Github Actions")
def test_google_search_counts_us(driver: Firefox):
    """
    C1365026, Test Google Search counts - urlbar US
    """
    # instantiate objects
    nav = Navigation(driver)
    nav.search("festival")
    sleep(5)
    u = Utilities()

    # Click on Raw JSON, switch tab and click on Raw Data
    about_telemetry = AboutTelemetry(driver).open()
    sleep(2)
    about_telemetry.get_element("category-raw").click()
    about_telemetry.switch_to_new_tab()
    about_telemetry.get_element("rawdata-tab").click()

    # Verify pings are recorded
    json_data = u.decode_url(driver)
    assert u.assert_json_value(
        json_data, '$..SEARCH_COUNTS.["google-b-1-d.urlbar"].sum', 1
    )
    assert u.assert_json_value(
        json_data,
        '$..["browser.search.content.urlbar"].["google:tagged:firefox-b-1-d"]',
        1,
    )
