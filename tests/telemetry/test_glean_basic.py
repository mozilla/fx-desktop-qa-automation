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


def glean_handler(rq: Request) -> Response:
    print(list(rq.headers.keys()))
    if "X-Debug-Id" in rq.headers.keys():
        print("URL:", rq.url)
        print("HEAD:", rq.headers)
        return Response({"id": rq.headers["X-Debug-Id"]}, status=200)
    else:
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
    print(f"ping: {ping}")
    driver.get("about:glean")
    ping_input = driver.find_element(By.ID, c.glean_ping_id)
    ba.clear_and_fill(ping_input, ping)
    ba.wait_on_element_contains_text(
        (By.CSS_SELECTOR, f"label[for='{c.glean_submit_id}'"), ping
    )
    driver.find_element(By.ID, c.glean_submit_id).click()
    # driver.execute_script(
    #     f"Services.fog.setTagPings('{ping}'); Services.fog.sendPing('metrics');"
    # )
    # Search 1 (Google)
    #driver.switch_to.new_window("tab")
    sleep(1)
    ba.search("trombone")
    # for rq in driver.requests:
    #     if "quicksuggest" in rq.url or "firefox.settings" in rq.url:
    #         continue
    #     print(rq.url, rq.headers, rq.body)
    #     print("----")
    #     if rq.response is not None:
    #         print(rq.response.status_code, rq.response.headers)
    #     else:
    #         print("null response")
    #     print("=====\n")
    ba.wait_on_title("Search")
    wait.until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "div[aria-label='About this result']")
        )
    )
    # Change default search engine
    # driver.switch_to.new_window("tab")
    driver.get("about:preferences")
    driver.find_element(By.ID, c.prefs_search_cat_id).click()
    engine_select = driver.find_element(By.ID, c.prefs_engine_dropdown_id)
    engine_select.click()
    list_item = driver.find_element(By.CSS_SELECTOR, "menuitem[label='Google']")
    list_item.click()
    list_item.send_keys(
        Keys.DOWN, Keys.DOWN, Keys.DOWN, Keys.RETURN
    )  # we hack because we care - clicking on these special elements doesn't always work
    sleep(1)
    # Search 2 (DDG)
    ba.search("trumpet")
    ba.wait_on_title("DuckDuckGo")
    wait.until(EC.visibility_of_element_located((By.ID, "more-results")))
