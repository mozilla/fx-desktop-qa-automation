from .helpers import by_id

ROOT = """
import pytest

@pytest.fixture()
def prefs():
    return ["root"]

@pytest.fixture()
def driver(prefs, timeout):
    return prefs

@pytest.fixture()
def timeout():
    return 10

@pytest.fixture(autouse=True)
def root_autouse():
    pass
"""


def test_fixture_inherited_from_parent_conftest(make_repo, run_inventory):
    repo = make_repo(
        {
            "conftest.py": ROOT,
            "tests/tabs/test_a.py": "def test_a(timeout):\n    pass\n",
        }
    )
    f = by_id(run_inventory(repo))["conftest.py::timeout"]
    assert f["tests_using_starfox"] == 1
    assert f["inheritance"] == {"same_location": 0, "inherited_from_parent": 1}


def test_nested_dependencies_resolve_from_the_test_location(make_repo, run_inventory):
    repo = make_repo(
        {
            "conftest.py": ROOT,
            "tests/tabs/conftest.py": """
                import pytest

                @pytest.fixture()
                def prefs():
                    return ["suite"]
            """,
            "tests/tabs/test_a.py": "def test_a(driver):\n    pass\n",
            "tests/menus/test_b.py": "def test_b(driver):\n    pass\n",
        }
    )
    inv = run_inventory(repo)
    tests = {t["id"]: t for t in inv["tests"]}
    tabs = tests["tests/tabs/test_a.py::test_a"]["fixtures_starfox"]
    menus = tests["tests/menus/test_b.py::test_b"]["fixtures_starfox"]
    assert "tests/tabs/conftest.py::prefs" in tabs and "conftest.py::prefs" not in tabs
    assert "conftest.py::prefs" in menus
    assert {
        "conftest.py::driver",
        "conftest.py::timeout",
        "conftest.py::root_autouse",
    } <= set(tabs)
    edges = {(e["from"], e["to"]) for e in inv["graph"]["starfox"]["edges"]}
    assert ("conftest.py::driver", "tests/tabs/conftest.py::prefs") in edges


def test_fixture_requesting_its_own_name_gets_the_parent(make_repo, run_inventory):
    repo = make_repo(
        {
            "conftest.py": ROOT,
            "tests/tabs/conftest.py": """
                import pytest

                @pytest.fixture()
                def prefs(prefs):
                    return prefs + ["suite"]
            """,
            "tests/tabs/test_a.py": "def test_a(prefs):\n    pass\n",
        }
    )
    inv = run_inventory(repo)
    fixtures = by_id(inv)
    assert fixtures["tests/tabs/conftest.py::prefs"]["shadows"] == "conftest.py::prefs"
    assert fixtures["conftest.py::prefs"]["tests_using_starfox"] == 1
    assert inv["unresolved_references"] == []


def test_missing_references_and_parametrized_names(make_repo, run_inventory):
    repo = make_repo(
        {
            "tests/tabs/test_a.py": """
                import pytest

                @pytest.fixture()
                def uses_param(region):
                    return region

                @pytest.mark.parametrize("region", ["US"])
                def test_a(uses_param, region, nope):
                    pass
            """,
        }
    )
    inv = run_inventory(repo)
    assert [r["name"] for r in inv["unresolved_references"]] == ["nope"]


def test_duplicate_fixture_names_across_suites(make_repo, run_inventory):
    same = "import pytest\n\n@pytest.fixture()\ndef helper():\n    return 1\n"
    repo = make_repo(
        {
            "tests/a/conftest.py": same,
            "tests/b/conftest.py": same,
            "tests/c/conftest.py": same.replace("return 1", "return 2"),
        }
    )
    (dup,) = run_inventory(repo)["duplicates"]
    assert (dup["name"], dup["definitions"], dup["distinct_implementations"]) == (
        "helper",
        3,
        2,
    )


def test_scopes_are_reported(make_repo, run_inventory):
    repo = make_repo(
        {
            "tests/a/conftest.py": """
                import pytest

                @pytest.fixture(scope="session")
                def s(): ...

                @pytest.fixture(scope="module")
                def m(): ...

                @pytest.fixture
                def f(): ...
            """,
            "tests/a/test_a.py": "def test_a(s, m, f):\n    pass\n",
        }
    )
    scopes = {f["name"]: f["scope"] for f in run_inventory(repo)["fixtures"]}
    assert scopes == {"s": "session", "m": "module", "f": "function"}


def test_autouse_only_applies_below_its_conftest(make_repo, run_inventory):
    repo = make_repo(
        {
            "tests/a/conftest.py": "import pytest\n\n@pytest.fixture(autouse=True)\ndef auto(): ...\n",
            "tests/a/test_a.py": "def test_a():\n    pass\n",
            "tests/b/test_b.py": "def test_b():\n    pass\n",
        }
    )
    tests = {t["id"]: t["fixtures_starfox"] for t in run_inventory(repo)["tests"]}
    assert tests["tests/a/test_a.py::test_a"] == ["tests/a/conftest.py::auto"]
    assert tests["tests/b/test_b.py::test_b"] == []


def test_getfixturevalue_requests_are_optional(make_repo, run_inventory):
    repo = make_repo(
        {
            "tests/a/conftest.py": """
                import pytest

                @pytest.fixture()
                def maybe(request):
                    if "extra" in request.fixturenames:
                        return request.getfixturevalue("extra")
            """,
            "tests/a/test_a.py": "def test_a(maybe):\n    pass\n",
        }
    )
    inv = run_inventory(repo)
    assert inv["unresolved_references"] == []
    assert inv["optional_requests_missing_after_migration"] == {
        "extra": ["tests/a/conftest.py::maybe"]
    }


def test_builtin_fixtures_resolve(make_repo, run_inventory):
    repo = make_repo(
        {"tests/a/test_a.py": "def test_a(tmp_path, request, monkeypatch):\n    pass\n"}
    )
    inv = run_inventory(repo)
    assert inv["unresolved_references"] == []
    assert inv["missing_after_migration"] == []
