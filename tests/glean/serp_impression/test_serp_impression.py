import logging

import pytest
from selenium.webdriver import Firefox

from modules.classes.glean import GleanAsserts
from modules.page_object import AboutGlean, AboutPrefs
from tests.glean.flows import run_action, run_entry
from tests.glean.utils import load_cases

data = load_cases(__file__)
METRIC = data["metric"]
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


def test_serp_impression(driver: Firefox, case: dict):
    prefs = AboutPrefs(driver, category="search")
    glean = AboutGlean(driver)
    params = case.get("params", {})

    engine = params.get("engine")
    if engine:
        prefs.open()
        prefs.search_engine_dropdown().select_option(engine)

    run_entry(driver, case["entry"], SEARCH_TERM, params)
    run_action(driver, case.get("action"), params)

    events = glean.poll_glean_metric(METRIC)
    expected = case["expected"]
    # Log/print captured ping so we can verify the right payload was asserted
    actual_payload = events[-1].get("extra", {}) if events else {}
    logging.info(
        "Glean %s: %d event(s), asserting payload (expected subset): %s",
        METRIC,
        len(events),
        expected,
    )
    logging.info("Glean %s: actual payload (event used): %s", METRIC, actual_payload)
    print(f"\n[Glean {METRIC}] events captured: {len(events)}")
    print(f"[Glean {METRIC}] expected (subset): {expected}")
    print(f"[Glean {METRIC}] actual payload:   {actual_payload}\n")
    GleanAsserts.assert_payload(METRIC, events, expected)
