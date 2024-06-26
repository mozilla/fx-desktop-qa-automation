import time
import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation
from modules.page_object import AboutTelemetry

from modules.util import Utilities

# unstable: for some reason cannot pass in Taskcluster Linux VM
@pytest.mark.unstable
def test_google_search_counts_us(driver: Firefox):
    """
    C1365026, Test Google Search counts - urlbar US
    """
    # instantiate objects
    nav = Navigation(driver).open()
    nav.search("festival")
    time.sleep(5)
    about_telemetry = AboutTelemetry(driver).open()
    u = Utilities()

    # Click on Raw JSON, switch tab and click on Raw Data
    about_telemetry.get_element("category-raw").click()
    about_telemetry.switch_tab()
    about_telemetry.get_element("rawdata-tab").click()

    # Verify pings are recorded
    json_data = u.decode_url(driver)
    assert u.assert_json_value(json_data, '$..SEARCH_COUNTS.["google-b-1-d.urlbar"].sum', 1)
    assert u.assert_json_value(json_data, '$..["browser.search.content.urlbar"].["google:tagged:firefox-b-1-d"]', 1)
