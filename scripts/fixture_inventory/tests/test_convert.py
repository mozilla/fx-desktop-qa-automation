import ast
import hashlib
import json
from types import SimpleNamespace

import pytest

from ..analysis import Analysis, Options
from ..convert import Converter, _tidy_blank_lines, main, write_outputs
from .helpers import write_files

FIREFOX_CONFTEST = """
import pytest


@pytest.fixture()
def prefs_list(add_to_prefs_list: list):
    \"\"\"List of prefs to send to main conftest.py driver fixture\"\"\"
    prefs = []
    prefs.extend(add_to_prefs_list)
    return prefs


@pytest.fixture()
def add_to_prefs_list():
    return []


@pytest.fixture(autouse=True)
def driver(prefs_list):
    yield prefs_list
"""

STARFOX_ROOT = """
import pytest


@pytest.fixture()
def driver(prefs_list, hard_quit):
    yield prefs_list


@pytest.fixture()
def hard_quit():
    return False


@pytest.fixture()
def needed_root():
    return 1


@pytest.fixture(scope="session", autouse=True)
def seeded():
    return 42
"""

SUITE_DEFAULTS = """
import pytest
from selenium.webdriver import Firefox


@pytest.fixture()
def suite_id():
    return ("1", "Suite")


@pytest.fixture()
def prefs_list(add_to_prefs_list: dict):
    \"\"\"List of prefs to send to main conftest.py driver fixture\"\"\"
    prefs = []
    prefs.extend(add_to_prefs_list)
    return prefs


@pytest.fixture()
def add_to_prefs_list():
    return []


# Ends Firefox without waiting.
@pytest.fixture()
def hard_quit():
    return True


@pytest.fixture(
    scope="function",
)
def helper(driver: Firefox):
    return driver
"""


def convert_all(tmp_path, files, rules=None, firefox=True, name="repo"):
    """Convert a small repo; return (repo, list of results)."""
    repo = write_files(tmp_path / name, {"tests/__init__.py": "", **files})
    ff = write_files(
        tmp_path / "firefox", {"testing/ui/tests/conftest.py": FIREFOX_CONFTEST}
    )
    site = tmp_path / "site"
    site.mkdir(exist_ok=True)
    opts = Options(
        repo=repo,
        firefox_root=ff,
        firefox_conftests=[ff / "testing/ui/tests/conftest.py"] if firefox else [],
        site_packages=[site],
    )
    rules = rules or SimpleNamespace(
        DROP={"hard_quit": "replaced by the driver default"}, MOVE_TO_SUITE={}
    )
    return repo, Converter(Analysis(opts).build(), rules).run()


def snapshot(repo):
    return {
        p: hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(repo.rglob("*"))
        if p.is_file()
    }


def build(tmp_path, files, rules=None):
    """Like convert_all, keyed by suite (for repos with one conftest per suite)."""
    repo, results = convert_all(tmp_path, files, rules)
    return repo, {r["suite"]: r for r in results}


def test_drops_defaults_firefox_provides_and_keeps_the_rest(tmp_path):
    _, results = build(
        tmp_path,
        {
            "conftest.py": STARFOX_ROOT,
            "tests/a/conftest.py": SUITE_DEFAULTS,
            "tests/a/test_a.py": "def test_a(helper, suite_id):\n    pass\n",
        },
    )
    r = results["a"]
    removed = {x["fixture"]: x["reason"] for x in r["removed"]}
    assert set(removed) == {"prefs_list", "add_to_prefs_list", "hard_quit"}
    assert removed["prefs_list"].startswith(
        "code-identical to testing/ui/tests/conftest.py"
    )
    assert removed["hard_quit"] == "replaced by the driver default"
    assert r["kept"] == ["suite_id", "helper"]
    names = {
        n.name for n in ast.parse(r["text"]).body if isinstance(n, ast.FunctionDef)
    }
    assert names == {"suite_id", "helper"}
    assert "Ends Firefox without waiting" not in r["text"]
    assert '@pytest.fixture(\n    scope="function",\n)\ndef helper' in r["text"]
    assert r["status"] == "ready"


def test_keeps_a_customised_prefs_list(tmp_path):
    custom = SUITE_DEFAULTS.replace("prefs = []", 'prefs = [("a.b", True)]')
    _, results = build(
        tmp_path,
        {
            "conftest.py": STARFOX_ROOT,
            "tests/a/conftest.py": custom,
            "tests/a/test_a.py": "def test_a(driver):\n    pass\n",
        },
    )
    assert "prefs_list" in results["a"]["kept"]


def test_removes_imports_only_removed_fixtures_used(tmp_path):
    # Firefox's only use is in hard_quit, which the DROP rule removes.
    suite = SUITE_DEFAULTS.replace(
        "def helper(driver: Firefox):", "def helper(driver):"
    ).replace("def hard_quit():", "def hard_quit(driver: Firefox):")
    _, results = build(
        tmp_path,
        {
            "conftest.py": STARFOX_ROOT,
            "tests/a/conftest.py": suite,
            "tests/a/test_a.py": "def test_a(helper):\n    pass\n",
        },
    )
    text = results["a"]["text"]
    assert "from selenium.webdriver import Firefox" not in text
    assert "import pytest" in text
    assert results["a"]["import_changes"] == ["removed unused import Firefox"]


def test_moves_a_root_fixture_into_its_suite_only(tmp_path):
    rules = SimpleNamespace(DROP={}, MOVE_TO_SUITE={"seeded": ["a"]})
    _, results = build(
        tmp_path,
        {
            "conftest.py": STARFOX_ROOT,
            "tests/a/conftest.py": "import pytest\n\n\n@pytest.fixture()\ndef x():\n    return 1\n",
            "tests/b/conftest.py": "import pytest\n\n\n@pytest.fixture()\ndef y():\n    return 1\n",
            "tests/a/test_a.py": "def test_a(x):\n    pass\n",
            "tests/b/test_b.py": "def test_b(y):\n    pass\n",
        },
        rules=rules,
    )
    assert results["a"]["moved_in"] == ["seeded"]
    assert (
        '@pytest.fixture(scope="session", autouse=True)\ndef seeded():'
        in results["a"]["text"]
    )
    assert results["b"]["moved_in"] == []


def test_rewrites_imports_from_reexport_shims(tmp_path):
    _, results = build(
        tmp_path,
        {
            "modules/__init__.py": "",
            "modules/browser_object.py": "from auto_fxui.browser_object import *\n",
            "tests/a/conftest.py": (
                "import pytest\nfrom modules.browser_object import TabBar\n\n\n"
                "@pytest.fixture()\ndef tabs(driver):\n    return TabBar(driver)\n"
            ),
            "tests/a/test_a.py": "def test_a(tabs):\n    pass\n",
        },
    )
    r = results["a"]
    assert "from auto_fxui.browser_object import TabBar" in r["text"]
    assert "modules" not in r["text"]
    assert not r["blockers"]


def test_reports_blockers_and_what_tests_still_need(tmp_path):
    _, results = build(
        tmp_path,
        {
            "conftest.py": STARFOX_ROOT,
            "data/page.html": "<p>hi</p>",
            "scripts/__init__.py": "",
            "scripts/secret.py": "def token():\n    return 'x'\n",
            "tests/a/conftest.py": (
                "from pathlib import Path\n\nimport pytest\nfrom scripts.secret import token\n\n\n"
                "@pytest.fixture()\ndef page():\n    return Path('data', 'page.html')\n\n\n"
                "@pytest.fixture()\ndef auth():\n    return token()\n\n\n"
                "@pytest.fixture()\ndef uses_root(needed_root):\n    return needed_root\n"
            ),
            "tests/a/test_a.py": "def test_a(page, auth, uses_root, needed_root):\n    pass\n",
        },
    )
    r = results["a"]
    assert r["status"] == "blocked"
    text = "\n".join(r["blockers"])
    assert "reads repo file 'data/page.html'" in text
    assert "imports scripts.secret, which the Firefox tree does not install" in text
    assert "auth: uses repo-local scripts.secret.token" in text
    assert "uses_root: requests 'needed_root'" in text
    assert r["tests_still_need"] == {"needed_root": 1}


def test_write_outputs_leaves_the_repo_untouched(tmp_path):
    repo, results = build(
        tmp_path,
        {
            "conftest.py": STARFOX_ROOT,
            "tests/a/conftest.py": SUITE_DEFAULTS,
            "tests/a/test_a.py": "def test_a(helper):\n    pass\n",
        },
    )

    before = snapshot(repo)
    out = tmp_path / "out"
    paths = write_outputs(list(results.values()), out, repo)
    assert snapshot(repo) == before
    assert (out / "a" / "conftest.py").read_text() == results["a"]["text"]
    assert {p.name for p in paths} >= {"conversion-report.json", "conversion-report.md"}
    compile(results["a"]["text"], "conftest.py", "exec")


# H1: the converter never writes into the repo it reads, or over earlier output.


def _suite_repo(tmp_path):
    return build(
        tmp_path,
        {
            "conftest.py": STARFOX_ROOT,
            "tests/a/conftest.py": SUITE_DEFAULTS,
            "tests/a/test_a.py": "def test_a(helper):\n    pass\n",
        },
    )


@pytest.mark.parametrize("inside", [".", "tests", "tests/a"])
def test_refuses_output_inside_the_repo(tmp_path, inside):
    repo, results = _suite_repo(tmp_path)
    before = (repo / "tests/a/conftest.py").read_text()
    with pytest.raises(ValueError, match="inside --repo"):
        write_outputs(list(results.values()), repo / inside, repo)
    assert (repo / "tests/a/conftest.py").read_text() == before


def test_refuses_non_empty_output_unless_overwrite(tmp_path):
    repo, results = _suite_repo(tmp_path)
    out = tmp_path / "out"
    out.mkdir()
    (out / "earlier.txt").write_text("keep me")
    with pytest.raises(FileExistsError, match="--overwrite"):
        write_outputs(list(results.values()), out, repo)
    write_outputs(list(results.values()), out, repo, overwrite=True)
    assert (out / "earlier.txt").read_text() == "keep me"


def test_cli_refuses_output_inside_repo_before_doing_any_work(tmp_path, capsys):
    repo, _ = _suite_repo(tmp_path)
    ff = tmp_path / "firefox" / "testing/ui/tests/conftest.py"
    code = main(
        [
            "--repo",
            str(repo),
            "--out",
            str(repo / "tests"),
            "--firefox-conftest",
            str(ff),
        ]
    )
    assert code == 2
    assert "inside --repo" in capsys.readouterr().err


# M1: only imports the conversion orphaned are removed.


def test_keeps_imports_that_were_already_unused(tmp_path):
    suite = (
        "import pytest\nimport side_effect_module\nfrom helpers import shared_fixture\n"
        "from selenium.webdriver import Firefox\n\n\n"
        "@pytest.fixture()\ndef add_to_prefs_list():\n    return []\n\n\n"
        "@pytest.fixture()\ndef uses(shared_fixture, driver: Firefox):\n    return driver\n"
    )
    _, results = build(
        tmp_path,
        {
            "tests/a/conftest.py": suite,
            "tests/a/test_a.py": "def test_a(uses):\n    pass\n",
        },
    )
    text = results["a"]["text"]
    assert "import side_effect_module" in text
    assert "from helpers import shared_fixture" in text
    assert "from selenium.webdriver import Firefox" in text
    assert results["a"]["import_changes"] == []


# M2: blank-line tidying leaves the inside of statements alone.


def test_tidy_keeps_blank_lines_inside_strings():
    src = (
        'import pytest\n\n\n\n\nJS = """a\n\n\n\nb"""\n\n\n\n\n'
        '@pytest.fixture()\ndef x():\n    """Doc.\n\n\n\n    more"""\n    return JS\n'
    )
    out = _tidy_blank_lines(src)
    assert '"""a\n\n\n\nb"""' in out
    assert "Doc.\n\n\n\n    more" in out
    assert "import pytest\n\n\nJS" in out
    assert out.count("\n\n\n@pytest.fixture") == 1


# M3: nested conftests keep their own path.


def test_nested_conftest_does_not_collide_with_its_suite(tmp_path):
    repo, rows = convert_all(
        tmp_path,
        {
            "tests/a/conftest.py": "import pytest\n\n\n@pytest.fixture()\ndef top():\n    return 1\n",
            "tests/a/deep/conftest.py": "import pytest\n\n\n@pytest.fixture()\ndef deep():\n    return 2\n",
            "tests/a/deep/test_d.py": "def test_d(top, deep):\n    pass\n",
        },
    )
    assert sorted(r["output"] for r in rows) == ["a/conftest.py", "a/deep/conftest.py"]
    out = tmp_path / "out"
    write_outputs(rows, out, repo)
    assert "def top" in (out / "a" / "conftest.py").read_text()
    assert "def deep" in (out / "a" / "deep" / "conftest.py").read_text()


# M4: a DROP rule is skipped while something still needs the fixture.


def test_drop_rule_skipped_while_a_kept_fixture_requests_it(tmp_path):
    suite = SUITE_DEFAULTS + (
        "\n\n@pytest.fixture()\ndef quitter(hard_quit):\n    return hard_quit\n"
    )
    _, results = build(
        tmp_path,
        {
            "conftest.py": STARFOX_ROOT,
            "tests/a/conftest.py": suite,
            "tests/a/test_a.py": "def test_a(quitter):\n    pass\n",
        },
    )
    r = results["a"]
    assert "hard_quit" in r["kept"]
    assert "hard_quit" not in {x["fixture"] for x in r["removed"]}
    assert "def hard_quit" in r["text"]
    assert any("DROP rule not applied" in b for b in r["blockers"])
    assert r["status"] == "blocked"


def test_drop_rule_skipped_while_a_test_requests_it(tmp_path):
    _, results = build(
        tmp_path,
        {
            "conftest.py": STARFOX_ROOT,
            "tests/a/conftest.py": SUITE_DEFAULTS,
            "tests/a/test_a.py": "def test_a(hard_quit):\n    pass\n",
        },
    )
    assert "def hard_quit" in results["a"]["text"]
    assert any("1 test(s) still use it" in b for b in results["a"]["blockers"])


# M5: a fixture only moves when the suite has everything it needs.

MOVE_ROOT = """
import pytest

SEED = 7


@pytest.fixture(autouse=True)
def seeded_from_constant():
    return SEED


@pytest.fixture(name="aliased")
def _aliased_impl(request):
    return request.node.name
"""


def test_move_refused_when_the_fixture_needs_root_names(tmp_path):
    rules = SimpleNamespace(DROP={}, MOVE_TO_SUITE={"seeded_from_constant": ["a"]})
    _, results = build(
        tmp_path,
        {
            "conftest.py": MOVE_ROOT,
            "tests/a/conftest.py": "import pytest\n\n\n@pytest.fixture()\ndef x():\n    return 1\n",
            "tests/a/test_a.py": "def test_a(x):\n    pass\n",
        },
        rules=rules,
    )
    r = results["a"]
    assert r["moved_in"] == []
    assert "seeded_from_constant" not in r["text"]
    assert any("needs ['SEED']" in b for b in r["blockers"])


def test_move_finds_a_fixture_by_its_fixture_name(tmp_path):
    rules = SimpleNamespace(DROP={}, MOVE_TO_SUITE={"aliased": ["a"]})
    _, results = build(
        tmp_path,
        {
            "conftest.py": MOVE_ROOT,
            "tests/a/conftest.py": "import pytest\n\n\n@pytest.fixture()\ndef x():\n    return 1\n",
            "tests/a/test_a.py": "def test_a(x):\n    pass\n",
        },
        rules=rules,
    )
    r = results["a"]
    assert r["moved_in"] == ["aliased"]
    assert '@pytest.fixture(name="aliased")\ndef _aliased_impl(request):' in r["text"]
    compile(r["text"], "conftest.py", "exec")


# M6: the converter needs the Firefox conftest to decide anything.


def test_converter_requires_a_firefox_conftest(tmp_path):
    with pytest.raises(ValueError, match="no Firefox conftest"):
        convert_all(
            tmp_path,
            {
                "tests/a/conftest.py": SUITE_DEFAULTS,
                "tests/a/test_a.py": "def test_a():\n    pass\n",
            },
            firefox=False,
        )


def test_cli_requires_a_firefox_conftest(tmp_path, capsys):
    repo, _ = _suite_repo(tmp_path)
    assert main(["--repo", str(repo), "--out", str(tmp_path / "o")]) == 2
    assert "--firefox-conftest is required" in capsys.readouterr().err


# Converting the converter's own output changes nothing.


def test_conversion_is_idempotent(tmp_path):
    files = {
        "conftest.py": STARFOX_ROOT,
        "tests/a/conftest.py": SUITE_DEFAULTS,
        "tests/a/test_a.py": "def test_a(helper, suite_id):\n    pass\n",
    }
    _, first = build(tmp_path / "one", files)
    again = {**files, "tests/a/conftest.py": first["a"]["text"]}
    _, second = build(tmp_path / "two", again)
    assert second["a"]["text"] == first["a"]["text"]
    assert second["a"]["removed"] == []
    assert second["a"]["import_changes"] == []


# Command line: writes conftests and a report, and never touches the repo.


def test_cli_writes_conftests_and_report(tmp_path, capsys):
    repo, _ = build(
        tmp_path,
        {
            "conftest.py": STARFOX_ROOT,
            "tests/a/conftest.py": (
                "import pytest\n\n\n@pytest.fixture()\n"
                "def uses_root(needed_root):\n    return needed_root\n"
            ),
            "tests/a/test_a.py": "def test_a(uses_root):\n    pass\n",
        },
    )
    ff = tmp_path / "firefox" / "testing/ui/tests/conftest.py"
    site = tmp_path / "site"
    before = snapshot(repo)
    out = tmp_path / "out"
    args = ["--repo", str(repo), "--out", str(out), "--firefox-conftest", str(ff)]
    assert main([*args, "--site-packages", str(site)]) == 0
    assert snapshot(repo) == before
    assert "0 ready, 1 blocked (static analysis; not run)" in capsys.readouterr().out
    assert (out / "a" / "conftest.py").is_file()
    report = json.loads((out / "conversion-report.json").read_text())
    assert report["note"].startswith("Static analysis only")
    assert report["root_fixtures_firefox_lacks"] == [
        {
            "name": "needed_root",
            "requested_by": ["uses_root"],
            "starfox_provides": ["conftest.py::needed_root"],
        }
    ]
    assert [c["status"] for c in report["conftests"]] == ["blocked"]
    md = (out / "conversion-report.md").read_text()
    assert "Static analysis only" in md
    assert "| needed_root | uses_root | conftest.py::needed_root |" in md


def test_cli_rejects_missing_firefox_files(tmp_path, capsys):
    repo, _ = _suite_repo(tmp_path)
    args = ["--repo", str(repo), "--out", str(tmp_path / "o")]
    assert main([*args, "--firefox-conftest", str(tmp_path / "nope.py")]) == 2
    assert "not a file" in capsys.readouterr().err
    assert not (tmp_path / "o").exists()
