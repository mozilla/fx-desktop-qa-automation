"""Regression tests: dependencies of fixtures missing in Firefox are followed."""

import pytest

from .helpers import fixture

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
def an(make_repo, analyse):
    repo = make_repo({"conftest.py": STARFOX_ROOT, **TESTS})
    return analyse(repo, firefox=FIREFOX)


def requesters(an, name):
    return an.ff_res.missing[name]["requesters"]


def test_missing_fixture_with_nested_dependencies(an):
    assert {"top", "middle", "leaf"} <= set(an.ff_res.missing)
    assert requesters(an, "top") == {"tests/a/test_nested.py::test_nested"}
    assert requesters(an, "leaf") == {"conftest.py::middle"}
    carried = an.ff_res.per_test["tests/a/test_nested.py::test_nested"]
    assert carried["carried_over"] == [
        "conftest.py::leaf",
        "conftest.py::middle",
        "conftest.py::top",
    ]


def test_missing_fixture_depending_on_another_missing_fixture(an):
    assert requesters(an, "start_time") == {"conftest.py::get_code"}
    assert an.ff_res.carried_over["get_code"] == {"conftest.py::get_code"}


def test_fixture_in_starfox_but_not_firefox(an):
    assert an.ff_res.carried_over["browser_name"] == {"conftest.py::browser_name"}
    # Its dependency is Firefox's own driver, so driver is not reported missing.
    assert "driver" not in an.ff_res.missing
    browser = an.ff_res.per_test["tests/a/test_browser.py::test_browser"]
    assert "testing/ui/tests/conftest.py::driver" in browser["fixtures"]


def test_consumer_replaced_by_firefox_drops_its_dependency(an):
    # STARfox's driver requested window_size; Firefox's driver does not.
    assert an.sf_res.used_by_tests["conftest.py::window_size"]
    assert not an.ff_res.used_by_tests.get("conftest.py::window_size")
    assert "window_size" not in an.ff_res.missing


def test_dependency_shared_by_multiple_consumers(an):
    shared = an.ff_res.missing["shared"]
    assert len(shared["tests"]) == 2
    assert shared["requesters"] == {"conftest.py::first", "conftest.py::second"}
    assert an.ff_res.carried_over["shared"] == {"conftest.py::shared"}


def test_dependency_every_test_overrides_is_still_required(an):
    # cleanup is carried over from the root and asks for pattern; the test
    # module's own pattern wins, so the root one is not carried.
    assert requesters(an, "cleanup") == {"tests/a/test_cleanup.py::test_cleanup"}
    assert "pattern" not in an.ff_res.missing
    override = fixture(an, "tests/a/test_cleanup.py::pattern")
    assert an.tests_using_after_migration(override) == 1


def test_optional_requests_and_autouse_are_not_carried_over(an):
    assert "extra" not in an.ff_res.missing
    assert an.ff_res.optional_missing["extra"] == {"tests/a/test_optional.py::maybe"}
    for t in an.ff_res.per_test.values():
        assert "conftest.py::side_effect" not in t["carried_over"]
