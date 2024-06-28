import time

import pytest
from seleniumwire.webdriver import Firefox

from modules.browser_object import Navigation
from modules.page_object import AboutTelemetry, GoogleSearch
from modules.util import Utilities

GSTATIC_ENDPOINT = "https://www.gstatic.com/_/mss/boq-search/_/js"


@pytest.fixture()
def add_prefs() -> list:
    return [
        ("browser.search.region", "US"),
    ]


@pytest.fixture()
def wire():
    return True


def test_google_search_counts_us(driver: Firefox):
    """
    C1365026, Test Google Search counts - urlbar US
    """
    # instantiate objects
    nav = Navigation(driver).open()
    google = GoogleSearch(driver)
    nav.search("festival")

    def telemetry_sent(rq):
        return (
            GSTATIC_ENDPOINT in rq.url
            and rq.response
            and rq.response.status_code == 200
        )

    longwait = google.custom_wait(timeout=50, poll_frequency=1)

    longwait.until(lambda d: any(telemetry_sent(rq) for rq in d.requests))

    about_telemetry = AboutTelemetry(driver).open()
    u = Utilities()

    # Click on Raw JSON, switch tab and click on Raw Data
    about_telemetry.get_element("category-raw").click()
    about_telemetry.switch_tab()
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
