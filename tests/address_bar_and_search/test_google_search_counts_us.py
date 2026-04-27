import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation
from modules.page_object import AboutTelemetry

SEARCH_TERM = "festival"
SEARCH_PROVIDER_PATH = '$..SEARCH_COUNTS.["google-b-1-d.urlbar"].sum'
SEARCH_TAG_PATH = '$..["browser.search.content.urlbar"].["google:tagged:firefox-b-1-d"]'


@pytest.fixture()
def test_case():
    return "3029528"


def test_google_search_counts_us(driver: Firefox, google_telemetry_runner):
    """
    C1365026 - Verify Google search counts in telemetry from the URL bar (US region).
    """
    nav = Navigation(driver)

    google_telemetry_runner(
        driver=driver,
        telemetry_cls=AboutTelemetry,
        search_action=lambda: nav.search(SEARCH_TERM),
        telemetry_expectations=[
            (SEARCH_PROVIDER_PATH, 1),
            (SEARCH_TAG_PATH, 1),
        ],
        after_search_wait=5,
        telemetry_load_wait=2,
    )
