from selenium.webdriver import Firefox

from modules.browser_object_about_telemetry import AboutTelemetry
from modules.browser_object_navigation import Navigation


def test_google_search_counts_us(driver: Firefox):
    """
        C1365026, Test Google Search counts - urlbar US
    """
    # instantiate objects
    nav = Navigation(driver).open()
    nav.search("festival")
    about_telemetry = AboutTelemetry(driver).open()

    # Click on Raw JSON, switch tab and click on Raw Data
    about_telemetry.get_element("category-raw").click()
    about_telemetry.switch_tab()
    about_telemetry.get_element("rawdata-tab").click()

    # Verify pings are recorded
    json_data = about_telemetry.decode_url()
    print(json_data)
    # assert json_data['payload']['stores']['main']['parent']['keyedHistograms']['SEARCH_COUNTS']['google-b-d.urlbar']['sum'] == 1
    # assert json_data['payload']['stores']['main']['parent']['keyedScalars']['browser.search.content.urlbar']['google:tagged:firefox-b-d'] == 1
    assert about_telemetry.find_value_in_json(json_data, "google:tagged:firefox-b-d", 1)
