import re

import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Glean
from modules.page_object import AboutPrefs
from tests.glean.flows import ENTRY_PREFS, SEARCH_TERM, run_abandonment
from tests.glean.utils import load_cases

data = load_cases(__file__)
METRIC = data["metric"]

# Each SERP event carries a UUID impression_id, e.g. "c85ccabf-7481-402e-b28d-22b4dc85561e"
IMPRESSION_ID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
)


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


def test_serp_abandonment(driver: Firefox, case: dict):
    """Verify serp.abandonment Glean event payload after a SERP is abandoned."""
    prefs = AboutPrefs(driver, category="search")
    glean = Glean(driver)
    params = case.get("params", {})

    engine = params.get("engine")
    if engine:
        prefs.open()
        prefs.search_engine_dropdown().select_option(engine)

    run_abandonment(driver, case["action"], SEARCH_TERM, params)

    events = glean.poll_glean_metric(METRIC, case["expected"])

    # The matched abandonment must carry a well-formed UUID impression_id
    impression_ids = [
        event.get("extra", {}).get("impression_id", "")
        for event in events
        if all(
            event.get("extra", {}).get(key) == value
            for key, value in case["expected"].items()
        )
    ]
    assert any(IMPRESSION_ID_RE.match(i) for i in impression_ids), (
        f"Expected a UUID impression_id in {METRIC}, got {impression_ids!r}"
    )
