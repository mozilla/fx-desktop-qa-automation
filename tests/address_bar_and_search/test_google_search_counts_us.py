import sys
from os import environ
from time import sleep

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation
from modules.page_object import AboutTelemetry
from modules.util import Utilities

# Constants
SEARCH_TERM = "festival"
SEARCH_PROVIDER_PATH = '$..SEARCH_COUNTS.["google-b-1-d.urlbar"].sum'
SEARCH_TAG_PATH = '$..["browser.search.content.urlbar"].["google:tagged:firefox-b-1-d"]'
WAIT_AFTER_SEARCH = 5
WAIT_TELEMETRY_LOAD = 2

# Conditional skip for GitHub Actions on macOS
MAC_GHA = environ.get("GITHUB_ACTIONS") == "true" and sys.platform.startswith("darwin")


@pytest.fixture()
def test_case():
    return "3029528"


@pytest.mark.skipif(MAC_GHA, reason="Test unstable in macOS GitHub Actions")
def test_google_search_counts_us(driver: Firefox):
    """
    C1365026: Verify Google search counts in telemetry from the URL bar (US region).
    """

    nav = Navigation(driver)
    nav.search(SEARCH_TERM)
    sleep(WAIT_AFTER_SEARCH)

    utils = Utilities()

    # === Open about:telemetry and navigate to raw JSON ===
    telemetry = AboutTelemetry(driver).open()
    sleep(WAIT_TELEMETRY_LOAD)
    telemetry.get_element("category-raw").click()
    telemetry.switch_to_new_tab()
    telemetry.get_element("rawdata-tab").click()

    # === Decode telemetry and validate search provider data ===
    json_data = utils.decode_url(driver)

    assert utils.assert_json_value(
        json_data, SEARCH_PROVIDER_PATH, 1
    ), f"Expected 1 Google search in path: {SEARCH_PROVIDER_PATH}"

    assert utils.assert_json_value(
        json_data, SEARCH_TAG_PATH, 1
    ), f"Expected 1 tagged Google search in path: {SEARCH_TAG_PATH}"
