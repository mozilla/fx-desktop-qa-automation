# bump
import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Glean
from modules.page_object import AboutPrefs
from tests.glean.flows import ENTRY_PREFS, SEARCH_TERM, run_action, run_entry
from tests.glean.utils import load_cases

data = load_cases(__file__)
METRIC = data["metric"]


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
    # Bing serves a bot-detection captcha on Linux CI for this flow's double-request pattern,
    # so the refinement never reaches a real SERP.
    if (
        sys_platform == "Linux"
        and case["entry"] == "follow_on_from_refine_on_incontent_search"
        and case.get("params", {}).get("engine") == "Bing"
    ):
        pytest.skip("Bing follow_on hits a bot-detection captcha on Linux CI")

    prefs = AboutPrefs(driver, category="search")
    glean = Glean(driver)
    params = case.get("params", {})

    engine = params.get("engine")
    if engine:
        prefs.open()
        prefs.search_engine_dropdown().select_option(engine)

    run_entry(driver, case["entry"], SEARCH_TERM, params)
    run_action(driver, case.get("action"), params)

    glean.poll_glean_metric(METRIC, case["expected"])
