import pytest
from selenium.webdriver import Firefox

from modules.classes.glean import GleanAsserts
from modules.page_object import AboutGlean, AboutPrefs
from tests.glean.flows import run_action, run_entry
from tests.glean.utils import load_cases

data = load_cases(__file__)
SEARCH_TERM = "test"


@pytest.fixture(params=data["cases"], ids=lambda c: c["id"])
def case(request):
    return request.param


@pytest.fixture()
def test_case(case):
    return case["id"]


@pytest.fixture()
def add_to_prefs_list(case):
    return [tuple(p) for p in case.get("prefs", [])]


def test_serp_ad(driver: Firefox, case: dict):
    prefs = AboutPrefs(driver, category="search")
    glean = AboutGlean(driver)
    params = case.get("params", {})
    metric = case["metric"]

    if params.get("engine"):
        prefs.open()
        prefs.search_engine_dropdown().select_option(params["engine"])

    run_entry(driver, case["entry"], SEARCH_TERM, params)
    run_action(driver, case["action"], params)

    events = glean.poll_glean_metric(metric)
    GleanAsserts.assert_payload(metric, events, case["expected"])
