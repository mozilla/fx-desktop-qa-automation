import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Glean
from modules.page_object import AboutPrefs
from tests.glean.flows import (
    AD_SEARCH_TERM,
    ENTRY_PREFS,
    SEARCH_TERM,
    block_if_bot_challenge,
    run_action,
    run_entry,
)
from tests.glean.utils import load_cases

data = load_cases(__file__)

# Metrics read as labeled counters ({label: count}); everything else is an event payload.
LABELED_COUNTER_METRICS = {
    "browserEngagementNavigation.searchbar",
    "browserSearchContent.searchbar",
    "browserSearchWithads.searchbar",
}
# Metrics that only record when the SERP serves ads, so they need a commercial query.
AD_METRICS = {
    "browserSearchWithads.searchbar",
    "serp.adImpression",
}
# Entries that pick their own engine in-flow, so no default-engine change is needed.
IN_FLOW_ENGINE_ENTRIES = {"searchbar_search_form"}
# Already the default engine, so selecting it in prefs is skipped.
DEFAULT_ENGINE = "Google"


@pytest.fixture(
    params=data["cases"],
    ids=lambda c: c["id"],
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


def test_misc_metrics(driver: Firefox, case: dict):
    """Verify a misc searchbar telemetry metric records the expected value."""
    prefs = AboutPrefs(driver, category="search")
    glean = Glean(driver)
    params = case.get("params", {})
    metric = case["metric"]
    expected = case["expected"]

    engine = params.get("engine")
    if (
        engine
        and engine != DEFAULT_ENGINE
        and case["entry"] not in IN_FLOW_ENGINE_ENTRIES
    ):
        prefs.open()
        prefs.search_engine_dropdown().select_option(engine)

    search_term = AD_SEARCH_TERM if metric in AD_METRICS else SEARCH_TERM

    try:
        run_entry(driver, case["entry"], search_term, params)
        run_action(driver, case.get("action"), params)

        if metric in LABELED_COUNTER_METRICS:
            for label, count in expected.items():
                glean.poll_glean_labeled_counter(metric, label, count)
            return
        events = glean.poll_glean_metric(metric, expected)
    except Exception:
        block_if_bot_challenge(driver)
        raise

    # Fields whose values are dynamic (ad counts, UUID impression_id) are checked for presence
    required_keys = case.get("expected_keys", [])
    if required_keys:
        assert any(
            all(key in event.get("extra", {}) for key in required_keys)
            for event in events
        ), f"Expected keys {required_keys} in {metric}, got {events!r}"
