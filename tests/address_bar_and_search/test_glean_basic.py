import gzip
import json
import re
from time import sleep

import pytest
from pytest_httpserver import HTTPServer
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from werkzeug.wrappers import Request, Response

from modules.browser_object import Navigation
from modules.page_object import AboutConfig, AboutGlean, AboutPrefs, GenericPage
from modules.util import Utilities

# Constants
SEARCH_TERM_GOOGLE = "trombone"
SEARCH_TERM_BING = "trumpet"
ENGINE_NAME_INITIAL = "Google"
ENGINE_NAME_UPDATED = "Bing"
EXPECTED_BING_LOCATOR = (By.ID, "b_context")
EXPECTED_SEARCH_LOCATOR = (By.CSS_SELECTOR, "div[role='navigation']")
PING_METRIC_PATH = ["metrics", "string", "search.engine.default.display_name"]
WAIT_PING_SECONDS = 1

# Globals (used for tracking ping verification)
pings_with_id = 0
ping_id_global = ""


@pytest.fixture()
def test_case():
    return "2234689"


def _verify_glean_ping(
    ping_actual: str, ping_expected: str, engine_actual: str, engine_expected: str
):
    assert ping_actual == ping_expected
    assert engine_actual.lower() == engine_expected.lower()


def glean_handler(request: Request) -> Response:
    global pings_with_id, ping_id_global

    if "X-Debug-Id" in request.headers:
        incoming_ping_id = request.headers["X-Debug-Id"]
        if request.data:
            decompressed = gzip.decompress(request.data).decode()
            body = json.loads(decompressed)
            engine_name = body
            for key in PING_METRIC_PATH:
                engine_name = engine_name[key]
            expected_engine = (
                ENGINE_NAME_INITIAL if pings_with_id == 0 else ENGINE_NAME_UPDATED
            )
            _verify_glean_ping(
                ping_actual=incoming_ping_id,
                ping_expected=ping_id_global,
                engine_actual=engine_name,
                engine_expected=expected_engine,
            )
            pings_with_id += 1

    return Response("", status=200)


@pytest.mark.unstable
# Still unstable sometime due to Captcha.
def test_glean_ping(driver: Firefox, httpserver: HTTPServer):
    """C2234689 - Test that Glean pings contain expected info"""

    global pings_with_id, ping_id_global
    utils = Utilities()

    # Setup mock server
    httpserver.expect_request(re.compile("^/")).respond_with_handler(glean_handler)

    # Configure Glean ping ID
    ping_id = utils.random_string(8)
    ping_id_global = ping_id
    about_glean = AboutGlean(driver)
    about_glean.open()
    about_glean.change_ping_id(ping_id)

    # Disable cookie banner
    about_config = AboutConfig(driver)
    about_config.change_config_value("cookiebanners.service.mode", 1)
    # Test is more stable if this is done here instead of prefs

    # Perform search using default engine (Google)
    page = GenericPage(driver, url="")
    nav = Navigation(driver)
    nav.search(SEARCH_TERM_GOOGLE)
    page.title_contains("Search")
    page.expect(EC.presence_of_element_located(EXPECTED_SEARCH_LOCATOR))

    # Change default engine to Bing
    prefs = AboutPrefs(driver, category="search")
    prefs.open()
    prefs.search_engine_dropdown().select_option(ENGINE_NAME_UPDATED)

    # Perform search using updated engine (Bing)
    nav.open()
    nav.search(SEARCH_TERM_BING)
    page.url_contains("bing.com")
    page.expect(EC.visibility_of_element_located(EXPECTED_BING_LOCATOR))

    # Send metrics ping
    with driver.context(driver.CONTEXT_CHROME):
        driver.execute_script('Services.fog.sendPing("metrics");')

    sleep(WAIT_PING_SECONDS)
    assert pings_with_id == 2
