import gzip
import json
import re
from time import sleep

from pytest_httpserver import HTTPServer
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from werkzeug.wrappers import Request, Response

from modules.browser_object import Navigation
from modules.page_object import AboutGlean, AboutPrefs
from modules.util import Utilities

PINGS_WITH_ID = 0
PING_ID = ""


def confirm_glean_correctness(
    ping_ground: str, ping_test: str, engine_ground: str, engine_test: str
) -> bool:
    assert ping_ground == ping_test
    assert engine_ground.lower() == engine_test.lower()


def glean_handler(rq: Request) -> Response:
    global PINGS_WITH_ID
    global PING_ID
    if "X-Debug-Id" in rq.headers.keys():
        ping_id = rq.headers["X-Debug-Id"]
        if rq.data:
            body = json.loads(gzip.decompress(rq.data).decode())
            engine_name = body["metrics"]["string"][
                "search.engine.default.display_name"
            ]
            if PINGS_WITH_ID == 0:
                engine_ground = "Google"
            else:
                engine_ground = "DuckDuckGo"
            confirm_glean_correctness(
                ping_ground=PING_ID,
                ping_test=ping_id,
                engine_ground=engine_ground,
                engine_test=engine_name,
            )
            PINGS_WITH_ID += 1
    return Response("", status=200)


def test_glean_ping(driver: Firefox, httpserver: HTTPServer):
    # C2234689
    global PINGS_WITH_ID
    global PING_ID
    u = Utilities()
    wait = WebDriverWait(driver, 30)

    # mock server
    httpserver.expect_request(re.compile("^/")).respond_with_handler(glean_handler)

    # Set ping name
    ping = u.random_string(8)
    PING_ID = ping
    about_glean = AboutGlean(driver).open()
    about_glean.change_ping_id(ping)

    # Search 1 (Google)
    nav = Navigation(driver).open()
    nav.search("trombone")
    nav.expect_in_content(EC.title_contains("Search"))
    nav.expect_in_content(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='navigation']"))
    )

    # Change default search engine
    about_prefs = AboutPrefs(driver, category="search").open()
    about_prefs.search_engine_dropdown().select_option("DuckDuckGo")

    # Search 2 (DDG)
    nav = Navigation(driver).open()
    (
        nav.search("trumpet")
        .expect_in_content(EC.title_contains("DuckDuckGo"))
        .expect_in_content(EC.visibility_of_element_located((By.ID, "more-results")))
    )

    # We could go back to about:glean, but this is faster
    with driver.context(driver.CONTEXT_CHROME):
        driver.execute_script('Services.fog.sendPing("metrics");')
    sleep(1)
    assert PINGS_WITH_ID == 2
