"""Regression tests: dependencies of fixtures missing in Firefox are followed."""

import pytest

from .helpers import by_id

STARFOX_ROOT = """
import pytest

@pytest.fixture()
def window_size():
    return "1x1"

@pytest.fixture()
def driver(window_size):
    yield window_size

@pytest.fixture()
def leaf():
    return 1

@pytest.fixture()
def middle(leaf):
    return leaf

@pytest.fixture()
def top(middle):
    return middle

@pytest.fixture()
def start_time():
    return "now"

@pytest.fixture()
def get_code(start_time):
    return start_time

@pytest.fixture()
def account(get_code):
    return get_code

@pytest.fixture()
def shared():
    return 1

@pytest.fixture()
def first(shared):
    return shared

@pytest.fixture()
def second(shared):
    return shared

@pytest.fixture()
def browser_name(driver):
    return driver

@pytest.fixture()
def pattern():
    return "never-matches"

@pytest.fixture()
def cleanup(pattern):
    return pattern

@pytest.fixture()
def never_used():
    return 1

@pytest.fixture()
def extra():
    return 1

@pytest.fixture(autouse=True)
def side_effect():
    pass
"""

FIREFOX = {
    "testing/ui/tests/conftest.py": """
        import pytest

        @pytest.fixture()
        def prefs_list():
            return []

        @pytest.fixture(autouse=True)
        def driver(prefs_list):
            yield prefs_list
    """,
}

TESTS = {
    "tests/a/test_nested.py": "def test_nested(top):\n    pass\n",
    "tests/a/test_chain.py": "def test_chain(account):\n    pass\n",
    "tests/a/test_shared.py": (
        "def test_one(first):\n    pass\n\n\ndef test_two(second):\n    pass\n"
    ),
    "tests/a/test_browser.py": "def test_browser(browser_name):\n    pass\n",
    "tests/a/test_cleanup.py": """
        import pytest

        @pytest.fixture()
        def pattern():
            return "report-*.pdf"

        def test_cleanup(cleanup):
            pass
    """,
    "tests/a/test_optional.py": """
        import pytest

        @pytest.fixture()
        def maybe(request):
            if "extra" in request.fixturenames:
                return request.getfixturevalue("extra")

        def test_optional(maybe):
            pass
    """,
}


@pytest.fixture()
def inv(make_repo, run_inventory):
    repo = make_repo({"conftest.py": STARFOX_ROOT, **TESTS})
    return run_inventory(repo, firefox=FIREFOX)


def missing(inv):
    return {m["name"]: m for m in inv["missing_after_migration"]}


def categories(inv):
    return {f["name"]: f["category"] for f in inv["fixtures"] if f["level"] == "root"}


def index_tests(inv):
    return {t["id"]: t for t in inv["tests"]}


def test_missing_fixture_with_nested_dependencies(inv):
    m = missing(inv)
    assert {"top", "middle", "leaf"} <= set(m)
    assert m["top"]["requested_directly_by_tests"] == 1
    assert not m["top"]["only_needed_through_other_missing_fixtures"]
    assert m["leaf"]["requested_by_fixtures"] == ["conftest.py::middle"]
    assert m["leaf"]["only_needed_through_other_missing_fixtures"]
    assert {categories(inv)[n] for n in ("top", "middle", "leaf")} == {
        "missing_required"
    }
    carried = index_tests(inv)["tests/a/test_nested.py::test_nested"]
    assert carried["carried_over_after_migration"] == [
        "conftest.py::leaf",
        "conftest.py::middle",
        "conftest.py::top",
    ]


def test_missing_fixture_depending_on_another_missing_fixture(inv):
    fixtures = by_id(inv)
    start_time = fixtures["conftest.py::start_time"]
    assert start_time["category"] == "missing_required"
    assert start_time["reasons"] == [
        "needed by 1 test(s) after migration",
        "declared as an argument by carried-over fixture(s) ['conftest.py::get_code']",
    ]
    assert missing(inv)["start_time"]["requested_by_fixtures"] == [
        "conftest.py::get_code"
    ]
    assert categories(inv)["get_code"] == "missing_required"


def test_fixture_in_starfox_but_not_firefox(inv):
    m = missing(inv)
    assert m["browser_name"]["starfox_providers"] == ["conftest.py::browser_name"]
    assert categories(inv)["browser_name"] == "missing_required"
    # Its dependency is Firefox's own driver, so driver is not reported missing.
    assert "driver" not in m
    assert categories(inv)["driver"] == "available_in_firefox"
    browser = index_tests(inv)["tests/a/test_browser.py::test_browser"]
    assert "testing/ui/tests/conftest.py::driver" in browser["fixtures_after_migration"]


def test_genuinely_redundant_vs_consumer_removed(inv):
    fixtures = by_id(inv)
    never_used = fixtures["conftest.py::never_used"]
    assert never_used["category"] == "potentially_redundant"
    assert never_used["reasons"] == ["not used by any analysed test"]
    window_size = fixtures["conftest.py::window_size"]
    assert window_size["category"] == "consumer_removed"
    assert "conftest.py::driver" in window_size["reasons"][0]


def test_dependency_shared_by_multiple_consumers(inv):
    shared = missing(inv)["shared"]
    assert shared["tests"] == 2
    assert shared["requested_by_fixtures"] == [
        "conftest.py::first",
        "conftest.py::second",
    ]
    assert shared["starfox_providers"] == ["conftest.py::shared"]
    assert categories(inv)["shared"] == "missing_required"


def test_dependency_every_test_overrides_is_still_required(inv):
    fixtures = by_id(inv)
    root = fixtures["conftest.py::pattern"]
    assert root["category"] == "missing_required"
    assert root["reasons"] == [
        "declared as an argument by carried-over fixture(s) ['conftest.py::cleanup']"
    ]
    override = fixtures["tests/a/test_cleanup.py::pattern"]
    assert override["category"] == "suite_local"
    assert override["tests_using_after_migration"] == 1


def test_optional_requests_and_autouse_are_not_carried_over(inv):
    assert "extra" not in missing(inv)
    assert inv["optional_requests_missing_after_migration"]["extra"] == [
        "tests/a/test_optional.py::maybe"
    ]
    assert categories(inv)["side_effect"] == "unresolved"
    for t in inv["tests"]:
        assert "conftest.py::side_effect" not in t["carried_over_after_migration"]
