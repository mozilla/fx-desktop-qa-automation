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
    assert (b.container, b.args) == ("TestGroup", ["shared"])
    (shared,) = info.fixtures
    assert (shared.scope, shared.level, shared.container, shared.args) == (
        "class",
        "class",
        "TestGroup",
        [],
    )


def test_facts_options_requests_and_repo_paths():
    info = parse(
        """
        from pathlib import Path

        import pytest

        PAGE = "data/pages/page.html"

        def helper():
            return "data/from_helper.json"

        @pytest.fixture()
        def everything(request):
            request.config.getoption("--my-flag")
            request.getfixturevalue("dynamic_one")
            return Path("data", "file.pdf"), PAGE, helper(), "https://example.com/x"
        """
    )
    (f,) = info.fixtures
    assert kinds(f.facts, "cli_option") == {("read", "--my-flag")}
    assert f.dynamic_requests() == ["dynamic_one"]
    assert kinds(f.facts, "asset") == {
        ("repo_path", "data/file.pdf"),
        ("repo_path", "data/pages/page.html"),
        ("repo_path", "data/from_helper.json"),
    }
    via = {x.detail for x in f.facts if x.value == "data/from_helper.json"}
    assert via == {"via helper()"}
    # Module-level code is recorded too: it stays in a converted conftest.
    assert kinds(info.facts, "asset") == {("repo_path", "data/pages/page.html")}


def test_parameter_shadowing_a_module_function_is_not_followed():
    info = parse(
        """
        import pytest

        @pytest.fixture()
        def driver():
            return "data/only_in_driver.html"

        @pytest.fixture()
        def uses_driver(driver):
            return driver.capabilities
        """
    )
    facts = {f.name: f.facts for f in info.fixtures}
    assert kinds(facts["driver"], "asset")
    assert not kinds(facts["uses_driver"], "asset")


def test_cli_options_defined():
    info = parse(
        """
        def pytest_addoption(parser):
            parser.addoption("--ci", action="store_true", dest="ci_mode")
            parser.getgroup("x")._addoption("-q2")
        """
    )
    assert {f.value for f in info.options_defined} == {"--ci", "ci_mode", "-q2"}


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


def test_syntax_error_is_recorded_not_raised():
    info = parse("def broken(:\n")
    assert info.parse_error and not info.fixtures
