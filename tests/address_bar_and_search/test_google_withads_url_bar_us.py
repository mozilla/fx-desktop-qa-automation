import pytest

from modules.browser_object import Navigation
from modules.page_object import AboutTelemetry

SEARCH_TERM = "iphone"
TELEMETRY_PATH = '$..["browser.search.withads.urlbar"].["google:tagged"]'


@pytest.fixture()
def test_case():
    return "3029577"


@pytest.fixture()
def add_to_prefs_list():
    return [("cookiebanners.service.mode", 1)]


def test_google_withads_url_bar_us(driver, google_telemetry_runner):
    """
    C1365070 - Verify Google with-ads URL bar telemetry (US region).
    """
    nav = Navigation(driver)

    google_telemetry_runner(
        driver=driver,
        telemetry_cls=AboutTelemetry,
        search_action=lambda: nav.search(SEARCH_TERM),
        telemetry_expectations=[(TELEMETRY_PATH, 1)],
        after_search_wait=5,
        telemetry_load_wait=5,
    )
