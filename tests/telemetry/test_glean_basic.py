from dataclasses import dataclass
import pytest
from time import sleep
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from modules.util import Utilities, BrowserActions
import requests
from pytest_httpserver import HTTPServer
from werkzeug.wrappers import Request
from werkzeug.wrappers import Response
import re
import gzip
import json


PINGS_WITH_ID = 0
PING_ID = ""


def confirm_glean_correctness(
    ping_ground: str, ping_test: str, engine_ground: str, engine_test: str
) -> bool:
    assert ping_ground == ping_test
    assert engine_ground.lower() == engine_test.lower()


def glean_handler(rq: Request) -> Response:
    if "X-Debug-Id" in rq.headers.keys():
        ping_id = rq.headers["X-Debug-Id"]
        if rq.data:
            body = json.loads(gzip.decompress(rq.data).decode())
            engine_name = body["metrics"]["string"][
                "search.engine.default.display_name"
            ]
            if PINGS_WITH_ID == 0:
                engine_ground = "Google"
                PINGS_WITH_ID += 1
            else:
                engine_ground = "DuckDuckGo"
            confirm_glean_correctness(
                ping_ground=PING_ID,
                ping_test=ping_id,
                engine_ground=engine_ground,
                engine_test=engine_name,
            )
    return Response("", status=200)


@dataclass
class LocalConstants:
    glean_ping_id: str = "tag-pings"
    glean_submit_id: str = "controls-submit"
    prefs_search_cat_id: str = "category-search"
    prefs_engine_dropdown_id: str = "defaultEngine"


def test_glean_ping(driver: Firefox, httpserver: HTTPServer):
    # C2234689
    u = Utilities()
    ba = BrowserActions(driver)
    c = LocalConstants()
    wait = WebDriverWait(driver, 30)

    # mock server
    httpserver.expect_request(re.compile("^/")).respond_with_handler(glean_handler)

    # Set ping name
    ping = u.random_string(8)
    PING_ID = ping
    print(f"ping: {ping}")
    driver.get("about:glean")
    ping_input = driver.find_element(By.ID, c.glean_ping_id)
    ba.clear_and_fill(ping_input, ping)
    ba.wait_on_element_contains_text(
        (By.CSS_SELECTOR, f"label[for='{c.glean_submit_id}'"), ping
    )
    driver.find_element(By.ID, c.glean_submit_id).click()

    # Search 1 (Google)
    sleep(1)
    ba.search("trombone")
    ba.wait_on_title("Search")
    wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='navigation']"))
    )

    # Change default search engine
    driver.get("about:preferences")
    driver.find_element(By.ID, c.prefs_search_cat_id).click()
    engine_select = driver.find_element(By.ID, c.prefs_engine_dropdown_id)
    engine_select.click()
    list_item = driver.find_element(By.CSS_SELECTOR, "menuitem[label='Google']")
    list_item.click()
    wait.until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "menuitem[_moz-menuactive='true']")
        )
    )
    list_item.send_keys(
        Keys.DOWN, Keys.DOWN, Keys.DOWN, Keys.RETURN
    )  # we hack because we care - clicking on these special elements doesn't always work
    sleep(1)

    # Search 2 (DDG)
    ba.search("trumpet")
    ba.wait_on_title("DuckDuckGo")
    wait.until(EC.visibility_of_element_located((By.ID, "more-results")))

    # We could go back to about:glean, but this is faster
    with driver.context(driver.CONTEXT_CHROME):
        driver.execute_script('Services.fog.sendPing("metrics");')
    sleep(1)
