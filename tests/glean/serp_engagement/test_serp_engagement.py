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

# Cases whose result-link click never reaches a real SERP because the engine serves a bot challenge
# to CI IPs instead. Keyed by platform, since the challenged set differs per platform.
BOT_CHALLENGE_SKIPS = {
    "Linux": ("3255530", "3255533"),
}


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


def test_serp_engagement(driver: Firefox, case: dict, sys_platform: str):
    """Verify serp.engagement Glean event payload after a SERP result is clicked."""
    if case["id"] in BOT_CHALLENGE_SKIPS.get(sys_platform, ()):
        pytest.skip("Engine serves a bot challenge instead of a SERP on CI")

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
