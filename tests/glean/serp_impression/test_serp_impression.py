import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Glean
from modules.page_object import AboutPrefs
from tests.glean.flows import (
    ENTRY_PREFS,
    RELATED_SEARCH_TERM,
    SEARCH_TERM,
    run_action,
    run_entry,
)
from tests.glean.utils import load_cases

data = load_cases(__file__)
METRIC = data["metric"]

# Cases whose on-page SERP interaction never reaches a real SERP because the engine serves a bot
# challenge to CI IPs instead. Keyed by platform, since the challenged set differs per platform.
BOT_CHALLENGE_SKIPS = {
    "Linux": ("3255447", "3255452", "3255477", "3255482"),
    "Darwin": ("3255477", "3255482"),
    "Windows": ("3255477", "3255482"),
}


@pytest.fixture(
    params=data["cases"],
    ids=lambda c: (
        f"{c['id']}-{c['entry']}" + (f"-{c['action']}" if c.get("action") else "")
    ),
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


def test_serp_impression(driver: Firefox, case: dict, sys_platform: str):
    """Verify serp.impression Glean event payload after a SERP is opened."""
    if case["id"] in BOT_CHALLENGE_SKIPS.get(sys_platform, ()):
        pytest.skip("Engine serves a bot challenge instead of a SERP on CI")

    prefs = AboutPrefs(driver, category="search")
    glean = Glean(driver)
    params = case.get("params", {})

    engine = params.get("engine")
    if engine:
        prefs.open()
        prefs.search_engine_dropdown().select_option(engine)

    # open_in_new_tab clicks an on-page related-search link, which only renders for a
    # commercial query; every other flow uses the default term.
    search_term = (
        RELATED_SEARCH_TERM if case.get("action") == "open_in_new_tab" else SEARCH_TERM
    )
    run_entry(driver, case["entry"], search_term, params)
    run_action(driver, case.get("action"), params)

    glean.poll_glean_metric(METRIC, case["expected"])
