from .helpers import fixture

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


def fixtures_of(an, test_id):
    return an.sf_res.per_test[test_id]["fixtures"]


def test_fixture_inherited_from_parent_conftest(make_repo, analyse):
    repo = make_repo(
        {
            "conftest.py": ROOT,
            "tests/tabs/test_a.py": "def test_a(timeout):\n    pass\n",
        }
    )
    an = analyse(repo)
    assert an.sf_res.used_by_tests["conftest.py::timeout"] == {
        "tests/tabs/test_a.py::test_a"
    }


def test_nested_dependencies_resolve_from_the_test_location(make_repo, analyse):
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
    an = analyse(repo)
    tabs = fixtures_of(an, "tests/tabs/test_a.py::test_a")
    menus = fixtures_of(an, "tests/menus/test_b.py::test_b")
    assert "tests/tabs/conftest.py::prefs" in tabs and "conftest.py::prefs" not in tabs
    assert "conftest.py::prefs" in menus
    assert {
        "conftest.py::driver",
        "conftest.py::timeout",
        "conftest.py::root_autouse",
    } <= set(tabs)
    assert ("conftest.py::driver", "tests/tabs/conftest.py::prefs") in an.sf_res.edges


def test_fixture_requesting_its_own_name_gets_the_parent(make_repo, analyse):
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
    an = analyse(repo)
    suite_prefs = fixture(an, "tests/tabs/conftest.py::prefs")
    assert an.sf.parent_of(suite_prefs).id == "conftest.py::prefs"
    assert an.sf_res.used_by_tests["conftest.py::prefs"]
    assert not an.sf_res.missing


def test_missing_references_and_parametrized_names(make_repo, analyse):
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
    assert set(analyse(repo).sf_res.missing) == {"nope"}


def test_autouse_only_applies_below_its_conftest(make_repo, analyse):
    repo = make_repo(
        {
            "tests/a/conftest.py": "import pytest\n\n@pytest.fixture(autouse=True)\ndef auto(): ...\n",
            "tests/a/test_a.py": "def test_a():\n    pass\n",
            "tests/b/test_b.py": "def test_b():\n    pass\n",
        }
    )
    an = analyse(repo)
    assert fixtures_of(an, "tests/a/test_a.py::test_a") == ["tests/a/conftest.py::auto"]
    assert fixtures_of(an, "tests/b/test_b.py::test_b") == []


def test_fixture_imported_from_a_helper_module_resolves(make_repo, analyse):
    repo = make_repo(
        {
            "tests/a/__init__.py": "",
            "tests/a/shared.py": "import pytest\n\n@pytest.fixture()\ndef page():\n    return 1\n",
            "tests/a/test_a.py": "from .shared import page\n\ndef test_a(page):\n    pass\n",
        }
    )
    an = analyse(repo)
    assert fixtures_of(an, "tests/a/test_a.py::test_a") == ["tests/a/shared.py::page"]


def test_getfixturevalue_requests_are_optional(make_repo, analyse):
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
    an = analyse(repo)
    assert not an.sf_res.missing
    assert an.ff_res.optional_missing == {"extra": {"tests/a/conftest.py::maybe"}}


def test_builtin_fixtures_resolve(make_repo, analyse):
    repo = make_repo(
        {"tests/a/test_a.py": "def test_a(tmp_path, request, monkeypatch):\n    pass\n"}
    )
    an = analyse(repo)
    assert not an.sf_res.missing
    assert not an.ff_res.missing
