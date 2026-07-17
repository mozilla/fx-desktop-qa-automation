import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Glean
from modules.page_object import AboutPrefs
from tests.glean.flows import (
    ENTRY_PREFS,
    SEARCH_TERM,
    run_action,
    run_entry,
)
from tests.glean.utils import load_cases

data = load_cases(__file__)
METRIC = data["metric"]


@pytest.fixture(
    params=data["cases"],
    ids=lambda c: f"{c['id']}-{c['entry']}-{c['action']}",
)
def case(request):
    """Parametrized fixture yielding one test case dict from cases.json."""
    return request.param


@pytest.fixture()
def test_case(case):
    """TestRail case ID for the current parametrized case."""
    return case["id"]


@pytest.fixture()
def add_to_prefs_list(case):
    """Per-case Firefox prefs to set before driver launch."""
    prefs = [tuple(p) for p in case.get("prefs", [])]
    prefs += ENTRY_PREFS.get(case["entry"], [])
    return prefs


def test_serp_engagement(driver: Firefox, case: dict):
    """Verify serp.engagement Glean event payload after a SERP result is clicked."""
    prefs = AboutPrefs(driver, category="search")
    glean = Glean(driver)
    params = case.get("params", {})

    engine = params.get("engine")
    if engine:
        prefs.open()
        prefs.search_engine_dropdown().select_option(engine)

    run_entry(driver, case["entry"], SEARCH_TERM, params)
    run_action(driver, case["action"], params)

    glean.poll_glean_metric(METRIC, case["expected"])
