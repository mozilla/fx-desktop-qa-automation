import textwrap

from ..parser import parse_module


def parse(source: str, kind="conftest", collect=False, entries=frozenset({"data"})):
    return parse_module(
        textwrap.dedent(source),
        "tests/suite/conftest.py" if kind == "conftest" else "tests/suite/test_x.py",
        kind=kind,
        origin="starfox",
        level="suite" if kind == "conftest" else "module",
        suite="suite",
        repo_entries=entries,
        collect_tests=collect,
    )


def kinds(findings, category):
    return {(f.kind, f.value) for f in findings if f.category == category}


def test_fixture_definition_fields():
    info = parse(
        """
        import pytest

        @pytest.fixture(scope="session", autouse=True, name="renamed")
        def original(dep, optional=1, *, kw):
            yield dep
        """
    )
    (f,) = info.fixtures
    assert (f.name, f.func_name, f.line, f.scope, f.autouse) == (
        "renamed",
        "original",
        5,
        "session",
        True,
    )
    assert f.args == ["dep", "kw"]
    assert f.is_generator


def test_fixture_decorator_forms_and_scopes():
    info = parse(
        """
        import pytest
        from pytest import fixture

        @pytest.fixture
        def plain(): ...

        @fixture(scope="module")
        def imported(): ...

        @pytest.fixture(scope=pick_scope)
        def computed(): ...

        @other.fixture
        def not_pytest(): ...

        def not_a_fixture(): ...
        """
    )
    scopes = {f.name: f.scope for f in info.fixtures}
    assert scopes == {"plain": "function", "imported": "module", "computed": "dynamic"}


def test_tests_parametrize_usefixtures_and_classes():
    info = parse(
        """
        import pytest

        pytestmark = pytest.mark.slow

        @pytest.mark.usefixtures("setup")
        @pytest.mark.parametrize("value, other", [(1, 2)])
        @pytest.mark.parametrize("via_fixture", [1], indirect=True)
        def test_a(driver, value, other, via_fixture):
            pass

        @pytest.mark.headed
        class TestGroup:
            @pytest.fixture(scope="class")
            def shared(self):
                return 1

            def test_b(self, shared):
                pass

        class Helper:
            def test_ignored(self):
                pass
        """,
        kind="test",
        collect=True,
    )
    a, b = info.tests
    assert a.args == ["driver", "via_fixture"]
    assert a.params == ["other", "value"]
    assert a.usefixtures == ["setup"]
    assert {m.value for m in a.markers} >= {"slow", "usefixtures", "parametrize"}
    assert (b.container, b.args) == ("TestGroup", ["shared"])
    assert {m.value for m in b.markers} == {"slow", "headed"}
    (shared,) = info.fixtures
    assert (shared.scope, shared.level, shared.container, shared.args) == (
        "class",
        "class",
        "TestGroup",
        [],
    )


def test_facts_env_options_assets_prefs_commands():
    info = parse(
        """
        import os
        import subprocess
        from os import environ
        from pathlib import Path

        import pytest

        PAGE = "data/pages/page.html"

        def helper():
            return os.getenv("HELPER_VAR")

        @pytest.fixture()
        def everything(request, options):
            environ["WRITTEN"] = "1"
            if "CHECKED" in os.environ:
                pass
            request.config.getoption("--my-flag")
            request.getfixturevalue("dynamic_one")
            options.set_preference("browser.pref", True)
            subprocess.run(["osascript", "-e", "x"])
            prefs = [("some.pref.name", False)]
            return Path("data", "file.pdf"), PAGE, helper(), "https://example.com/x"
        """
    )
    (f,) = info.fixtures
    assert kinds(f.facts, "env_var") == {
        ("write", "WRITTEN"),
        ("read", "CHECKED"),
        ("read", "HELPER_VAR"),
    }
    assert kinds(f.facts, "cli_option") == {("read", "--my-flag")}
    assert kinds(f.facts, "fixture_request") == {("getfixturevalue", "dynamic_one")}
    assert kinds(f.facts, "webdriver") >= {
        ("pref", "browser.pref"),
        ("pref", "some.pref.name"),
    }
    assert kinds(f.facts, "command") == {("subprocess.run", "osascript")}
    assets = kinds(f.facts, "asset")
    assert ("repo_path", "data/file.pdf") in assets
    assert ("repo_path", "data/pages/page.html") in assets
    assert ("url", "https://example.com/x") in assets
    via = {x.detail for x in f.facts if x.value == "HELPER_VAR"}
    assert via == {"via helper()"}


def test_parameter_shadowing_a_module_function_is_not_followed():
    info = parse(
        """
        import os
        import pytest

        @pytest.fixture()
        def driver():
            return os.environ.get("ONLY_IN_DRIVER")

        @pytest.fixture()
        def uses_driver(driver):
            return driver.capabilities
        """
    )
    facts = {f.name: f.facts for f in info.fixtures}
    assert not kinds(facts["uses_driver"], "env_var")


def test_hooks_options_markers_and_funcargs():
    info = parse(
        """
        def pytest_addoption(parser):
            parser.addoption("--ci", action="store_true", dest="ci_mode")
            parser.getgroup("x")._addoption("-q2")

        def pytest_configure(config):
            config.addinivalue_line("markers", "headed: needs a display")

        def pytest_exception_interact(node, call, report):
            node.funcargs.get("driver")
        """
    )
    assert [h.name for h in info.hooks] == [
        "pytest_addoption",
        "pytest_configure",
        "pytest_exception_interact",
    ]
    assert {f.value for f in info.options_defined} == {"--ci", "ci_mode", "-q2"}
    assert [f.value for f in info.markers_registered] == ["headed"]
    assert kinds(info.hooks[2].facts, "fixture_request") == {("funcargs", "driver")}


def test_fingerprint_covers_same_module_constants():
    template = """
        import pytest
        TIMEOUT = {value}

        @pytest.fixture()
        def wait():
            \"\"\"Docstrings do not count.\"\"\"
            return TIMEOUT
        """
    a = parse(template.format(value=5)).fixtures[0]
    b = parse(template.format(value=5).replace("do not count", "differ")).fixtures[0]
    c = parse(template.format(value=10)).fixtures[0]
    assert a.fingerprint == b.fingerprint
    assert a.fingerprint != c.fingerprint


def test_arg_usage_hints():
    info = parse(
        """
        import pytest

        @pytest.fixture()
        def consumer(flag, case, meta):
            if flag:
                pass
            meta["case"] = case
        """
    )
    usage = info.fixtures[0].arg_usage
    assert usage["flag"] == ["condition"]
    assert usage["case"] == ["stored in meta[...]"]


def test_syntax_error_is_recorded_not_raised():
    info = parse("def broken(:\n")
    assert info.parse_error and not info.fixtures
