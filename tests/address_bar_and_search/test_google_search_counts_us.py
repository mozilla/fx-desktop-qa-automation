import time

from selenium.webdriver import Firefox

from modules.browser_object_about_telemetry import AboutTelemetry
from modules.browser_object_navigation import Navigation
from jsonpath_ng import parse


def test_google_search_counts_us(driver: Firefox):
    """
        C1365026, Test Google Search counts - urlbar US
    """
    # instantiate objects
    nav = Navigation(driver).open()
    nav.search("festival")
    time.sleep(5)
    about_telemetry = AboutTelemetry(driver).open()


    # Click on Raw JSON, switch tab and click on Raw Data
    about_telemetry.get_element("category-raw").click()
    about_telemetry.switch_tab()
    about_telemetry.get_element("rawdata-tab").click()

    # Verify pings are recorded
    json_data = about_telemetry.decode_url()
    expr = parse('$..SEARCH_COUNTS.["google-b-1-d.urlbar"].sum')
    match = expr.find(json_data)
    assert match[0].value == 1
    expr2 = parse('$..["browser.search.content.urlbar"].["google:tagged:firefox-b-1-d"]')
    match2 = expr2.find(json_data)
    assert match2[0].value == 1
