import pytest
from selenium.webdriver import Firefox

from modules.browser_object_navigation import Navigation
from modules.page_object_about_pages import AboutConfig, AboutTelemetry

SEARCH_TERM = "iphone"
TELEMETRY_PATH = '$..keyedScalars.["browser.search.adclicks.urlbar"].["google:tagged"]'


@pytest.fixture()
def test_case():
    return "3029662"


def test_sap_google_adclick(driver: Firefox, google_telemetry_runner):
    """
    C1365108 - Verify Google ad click from URL bar is recorded in telemetry (US region).
    """
    nav = Navigation(driver)
    about_config = AboutConfig(driver)

    about_config.edit_config_value("cookiebanners.service.mode", 1)

    google_telemetry_runner(
        driver=driver,
        telemetry_cls=AboutTelemetry,
        search_action=lambda: nav.search(SEARCH_TERM),
        post_search_action=lambda: nav.get_element("search-result").click(),
        telemetry_expectations=[(TELEMETRY_PATH, 1)],
        after_search_wait=5,
        after_action_wait=2,
        telemetry_load_wait=2,
    )
