from .helpers import fixture

STARFOX_ROOT = """
import os
import pytest
from modules.secrets import get_secret

@pytest.fixture()
def sys_platform():
    return os.name

@pytest.fixture()
def secret():
    return get_secret()

@pytest.fixture()
def channel(request):
    return request.config.getoption("--fx-channel")

@pytest.fixture()
def pattern():
    return "never-matches"

@pytest.fixture()
def cleanup(pattern):
    return pattern
"""

FIREFOX = {
    "testing/ui/tests/conftest.py": """
        import pytest

        def pytest_addoption(parser):
            parser.addoption("--headless", action="store_true")

        @pytest.fixture()
        def same_code():
            return 1

        @pytest.fixture()
        def different_code():
            return 2

        @pytest.fixture()
        def prefs_list():
            return []

        @pytest.fixture(autouse=True)
        def driver(prefs_list):
            yield prefs_list
    """,
}

SUITE = """
import pytest

@pytest.fixture()
def same_code():
    return 1

@pytest.fixture()
def different_code():
    return 1

@pytest.fixture()
def needs_root(sys_platform):
    return sys_platform

@pytest.fixture()
def uses_cleanup(cleanup):
    return cleanup

@pytest.fixture()
def headless(request):
    return request.config.getoption("--headless")

@pytest.fixture()
def unused():
    return 1
"""

TEST_FILE = """
import pytest

@pytest.fixture()
def pattern():
    return "report-*.pdf"

def test_a(same_code, different_code, needs_root, uses_cleanup, headless):
    pass

def test_b(secret, channel):
    pass
"""


def build(make_repo, analyse, extra=None):
    repo = make_repo(
        {
            "modules/__init__.py": "",
            "modules/secrets.py": "def get_secret():\n    return 1\n",
            "conftest.py": STARFOX_ROOT,
            "tests/tabs/conftest.py": SUITE,
            "tests/tabs/test_a.py": TEST_FILE,
            **(extra or {}),
        }
    )
    return analyse(repo, firefox=FIREFOX)


def test_only_identical_code_counts_as_a_firefox_twin(make_repo, analyse):
    an = build(make_repo, analyse)
    same = fixture(an, "tests/tabs/conftest.py::same_code")
    different = fixture(an, "tests/tabs/conftest.py::different_code")
    assert an.firefox_twin(same).id == "testing/ui/tests/conftest.py::same_code"
    assert an.firefox_twin(different) is None


def test_starfox_parent_is_not_a_firefox_twin(make_repo, analyse):
    # Identical to the STARfox root fixture it shadows, but Firefox lacks one.
    copy = "import os\nimport pytest\n\n@pytest.fixture()\ndef sys_platform():\n    return os.name\n"
    an = build(make_repo, analyse, {"tests/menus/conftest.py": copy})
    local = fixture(an, "tests/menus/conftest.py::sys_platform")
    assert an.firefox_twin(local) is None
    assert an.cleanup_note(local).startswith("code-identical to conftest.py:")


def test_starfox_specific_reasons(make_repo, analyse):
    an = build(make_repo, analyse)
    secret = an.starfox_specific_reasons(fixture(an, "conftest.py::secret"))
    channel = an.starfox_specific_reasons(fixture(an, "conftest.py::channel"))
    headless = fixture(an, "tests/tabs/conftest.py::headless")
    assert "uses repo-local modules.secrets.get_secret" in secret[0]
    assert "reads CLI option --fx-channel that Firefox does not define" in channel[0]
    assert an.starfox_specific_reasons(headless) == []


def test_tests_package_helper_imports_are_followed(make_repo, analyse):
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
    an = analyse(repo)
    (reason,) = an.starfox_specific_reasons(fixture(an, "tests/glean/test_a.py::case"))
    assert "which imports STARfox-only ['manifests.key']" in reason


def test_missing_requests_and_cleanup_notes(make_repo, analyse):
    an = build(make_repo, analyse)
    needs_root = fixture(an, "tests/tabs/conftest.py::needs_root")
    assert an.missing_requests(needs_root) == ["sys_platform"]
    assert an.cleanup_note(needs_root) is None
    unused = fixture(an, "tests/tabs/conftest.py::unused")
    assert an.cleanup_note(unused) == "not used by any analysed test"


def test_firefox_lacks_module(make_repo, analyse):
    an = build(make_repo, analyse)
    an_with_site = analyse(
        an.repo,
        firefox={**FIREFOX, "python/sites/ui.txt": "pth:testing/mozbase/mozinfo\n"},
    )
    assert an.firefox_lacks_module("modules")
    assert not an.firefox_lacks_module("json")
    # Without a Firefox site file, third-party availability is assumed.
    assert not an.firefox_lacks_module("selenium")
    assert an_with_site.firefox_lacks_module("selenium")


def test_root_gaps_follow_carried_fixtures(make_repo, analyse):
    an = build(make_repo, analyse)
    gaps = {g["name"]: g for g in an.root_gaps()}
    # Test-only needs (secret, channel) are not suite conftest gaps.
    assert set(gaps) == {"sys_platform", "cleanup", "pattern"}
    assert gaps["sys_platform"]["requested_by"] == ["needs_root"]
    assert gaps["sys_platform"]["starfox_provides"] == ["conftest.py::sys_platform"]
    # Tests override pattern, but cleanup still declares it once in Firefox's root.
    assert gaps["pattern"]["requested_by"] == ["cleanup"]
    assert gaps["pattern"]["starfox_provides"] == ["conftest.py::pattern"]
