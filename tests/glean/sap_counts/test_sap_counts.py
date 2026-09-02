import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Glean
from modules.page_object import AboutPrefs
from tests.glean.flows import (
    ENTRY_PREFS,
    SEARCH_TERM,
    block_if_bot_challenge,
    run_entry,
)
from tests.glean.utils import load_cases, skip_if_unstable

data = load_cases(__file__)
METRIC = data["metric"]


@pytest.fixture(
    params=data["cases"],
    ids=lambda c: f"{c['id']}-{c['params']['engine']}-{c['entry']}",
)
def case(request):
    """Parametrized fixture yielding one test case dict from cases.json."""
    skip_if_unstable(request.param)
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


def test_sap_counts(driver: Firefox, case: dict):
    """Verify sap.counts records the access point a search was issued from."""
    prefs = AboutPrefs(driver, category="search")
    glean = Glean(driver)
    params = case["params"]

    prefs.open()
    prefs.search_engine_dropdown().select_option(params["engine"])

    try:
        run_entry(driver, case["entry"], SEARCH_TERM, params)

        glean.poll_glean_metric(METRIC, case["expected"])
    except Exception:
        block_if_bot_challenge(driver)
        raise
