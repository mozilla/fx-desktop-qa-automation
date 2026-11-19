from .helpers import by_id

STARFOX_ROOT = """
import os
import pytest
from modules.secrets import get_secret

@pytest.fixture()
def sys_platform():
    return os.name

@pytest.fixture()
def same_code():
    return 1

@pytest.fixture()
def different_code():
    return 1

@pytest.fixture()
def unused():
    return 1

@pytest.fixture()
def window_size():
    return "1x1"

@pytest.fixture()
def hard_quit():
    return False

@pytest.fixture(autouse=True)
def side_effect():
    os.environ["X"] = "1"

@pytest.fixture()
def secret():
    return get_secret()

@pytest.fixture()
def channel(request):
    return request.config.getoption("--fx-channel")

@pytest.fixture()
def driver(window_size, hard_quit):
    if hard_quit:
        pass
    yield window_size
"""

FIREFOX = {
    "testing/ui/tests/conftest.py": """
        import pytest

        @pytest.fixture()
        def same_code():
            return 1

        @pytest.fixture()
        def different_code():
            return 2

        @pytest.fixture()
        def prefs_list():
            return []

        @pytest.fixture()
        def driver(prefs_list):
            yield prefs_list
    """,
}


def build(make_repo, run_inventory, extra=None):
    repo = make_repo(
        {
            "modules/__init__.py": "",
            "modules/secrets.py": "def get_secret():\n    return 1\n",
            "conftest.py": STARFOX_ROOT,
            "tests/tabs/conftest.py": """
                import pytest

                @pytest.fixture()
                def prefs_list():
                    return []

                @pytest.fixture()
                def needs_root(sys_platform):
                    return sys_platform
            """,
            "tests/tabs/test_a.py": """
                import pytest

                @pytest.fixture()
                def hard_quit():
                    return True

                def test_a(driver, sys_platform, same_code, different_code, secret, channel):
                    pass

                def test_b(needs_root):
                    pass
            """,
            **(extra or {}),
        }
    )
    return run_inventory(repo, firefox=FIREFOX)


def test_root_categories(make_repo, run_inventory):
    inv = build(make_repo, run_inventory)
    cats = {f["name"]: f["category"] for f in inv["fixtures"] if f["level"] == "root"}
    assert cats == {
        "sys_platform": "missing_required",
        "same_code": "available_in_firefox",
        "different_code": "available_in_firefox",
        "unused": "potentially_redundant",
        "window_size": "consumer_removed",
        "hard_quit": "unresolved",
        "side_effect": "unresolved",
        "secret": "starfox_specific",
        "channel": "starfox_specific",
        "driver": "available_in_firefox",
    }


def test_equivalence_is_only_claimed_for_identical_code(make_repo, run_inventory):
    fixtures = by_id(build(make_repo, run_inventory))
    same = fixtures["conftest.py::same_code"]
    diff = fixtures["conftest.py::different_code"]
    assert same["firefox_equivalent"]["status"] == "code_identical"
    assert diff["firefox_equivalent"]["status"] == "same_name_code_differs"
    assert any("code differs" in n for n in diff["notes"])


def test_reasons_explain_the_category(make_repo, run_inventory):
    fixtures = by_id(build(make_repo, run_inventory))
    assert (
        "Firefox replaces them with its own fixtures"
        in fixtures["conftest.py::window_size"]["reasons"][0]
    )
    assert (
        "override it to configure ['conftest.py::driver']"
        in fixtures["conftest.py::hard_quit"]["reasons"][0]
    )
    assert "condition" in fixtures["conftest.py::hard_quit"]["reasons"][0]
    assert fixtures["conftest.py::side_effect"]["reasons"][0].startswith("autouse")
    assert (
        "modules.secrets"
        in fixtures["conftest.py::secret"]["starfox_specific_reasons"][0]
    )
    assert (
        "--fx-channel"
        in fixtures["conftest.py::channel"]["starfox_specific_reasons"][0]
    )


def test_local_fixture_categories(make_repo, run_inventory):
    fixtures = by_id(build(make_repo, run_inventory))
    suite_prefs = fixtures["tests/tabs/conftest.py::prefs_list"]
    assert suite_prefs["category"] == "potentially_redundant"
    assert "code-identical to testing/ui/tests/conftest.py" in suite_prefs["reasons"][0]
    override = fixtures["tests/tabs/test_a.py::hard_quit"]
    assert override["category"] == "consumer_removed"
    assert "Firefox replaces them" in override["reasons"][0]
    blocked = fixtures["tests/tabs/conftest.py::needs_root"]
    assert blocked["category"] == "suite_local"
    assert blocked["blocked_after_migration_by"] == ["sys_platform"]


def test_missing_after_migration_lists_providers(make_repo, run_inventory):
    inv = build(make_repo, run_inventory)
    missing = {m["name"]: m for m in inv["missing_after_migration"]}
    assert set(missing) == {"sys_platform", "secret", "channel"}
    assert missing["sys_platform"]["tests"] == 2
    assert missing["sys_platform"]["starfox_providers"] == ["conftest.py::sys_platform"]
    assert missing["sys_platform"]["requested_by_fixtures"] == [
        "tests/tabs/conftest.py::needs_root"
    ]
    assert not missing["sys_platform"]["also_missing_in_starfox"]


def test_cli_option_defined_in_firefox_is_not_starfox_specific(
    make_repo, run_inventory
):
    repo = make_repo(
        {
            "conftest.py": """
                import pytest

                @pytest.fixture()
                def headless(request):
                    return request.config.getoption("--headless")
            """,
            "tests/a/test_a.py": "def test_a(headless):\n    pass\n",
        }
    )
    firefox = {
        "testing/ui/tests/conftest.py": """
            def pytest_addoption(parser):
                parser.addoption("--headless", action="store_true")
        """
    }
    f = by_id(run_inventory(repo, firefox=firefox))["conftest.py::headless"]
    assert f["category"] == "missing_required"
    assert f["starfox_specific_reasons"] == []


def test_tests_package_helper_imports_are_followed(make_repo, run_inventory):
    repo = make_repo(
        {
            "manifests/__init__.py": "",
            "manifests/key.py": "def sysname():\n    return 'x'\n",
            "tests/glean/__init__.py": "",
            "tests/glean/utils.py": "from manifests.key import sysname\n\ndef load():\n    return sysname()\n",
            "tests/glean/test_a.py": """
                import pytest
                from tests.glean.utils import load

                @pytest.fixture()
                def case():
                    return load()

                def test_a(case):
                    pass
            """,
        }
    )
    f = by_id(run_inventory(repo))["tests/glean/test_a.py::case"]
    assert f["category"] == "starfox_specific"
    assert "manifests.key" in f["starfox_specific_reasons"][0]
