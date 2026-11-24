"""
Static fixture analysis behind the converter.

Parses STARfox, the Firefox conftests, installed plugins and pytest itself with
``ast`` (nothing is imported), then resolves every test's fixtures in two
worlds: STARfox as it is, and Firefox after migration (STARfox root conftests
replaced by the Firefox ones). "Code-identical" means the same code, including
same-module helpers and constants; it does not prove the same behaviour.
"""

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

from .discovery import discover
from .environment import Environment, parse_firefox_sites, stdlib_modules
from .models import Finding, FixtureDef, ModuleInfo
from .parser import parse_module
from .resolver import World


@dataclass
class Options:
    repo: Path
    tests_dir: str = "tests"
    exclude_suites: tuple[str, ...] = ()
    firefox_conftests: list[Path] = field(default_factory=list)
    firefox_root: Path | None = None
    firefox_sites: list[Path] = field(default_factory=list)
    site_packages: list[Path] | None = None


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def option_keys(flag: str) -> set[str]:
    """A CLI option as written and as its dest, e.g. --run-headless and run_headless."""
    return {flag, flag.lstrip("-").replace("-", "_")}


def _dotted(rel: str) -> str:
    parts = PurePosixPath(rel).with_suffix("").parts
    return ".".join(parts[:-1] if parts[-1] == "__init__" else parts)


class Analysis:
    def __init__(self, opts: Options):
        self.opts = opts
        self.notes: list[str] = []

    def build(self) -> "Analysis":
        self._parse_repo()
        self._parse_firefox()
        self._parse_environment()
        self._build_worlds()
        self.tests = [t for m in self.modules for t in m.tests]
        self.sf_res = self.sf.resolve(self.tests)
        self.ff_res = self.ff.resolve(self.tests)
        self.firefox_options = {
            k
            for m in self.ff_modules
            + self.builtins
            + [m for d, ms in self.plugins.items() if d in self.ff_dists for m in ms]
            for f in m.options_defined
            for k in option_keys(f.value)
        }
        self.helper_starfox_imports = self._helper_starfox_imports()
        return self

    # Parsing

    def _parse_repo(self):
        self.layout = layout = discover(
            self.opts.repo, self.opts.tests_dir, exclude_suites=self.opts.exclude_suites
        )
        self.repo = layout.repo
        self.tests_rel = layout.rel(layout.tests_dir)

        def parse(path, kind, level, collect=False):
            return parse_module(
                _read(path),
                layout.rel(path),
                kind=kind,
                origin="starfox",
                level=level,
                suite=layout.suite_of(path),
                collect_tests=collect,
                repo_entries=layout.repo_entries,
            )

        self.modules: list[ModuleInfo] = (
            [parse(p, "conftest", "root") for p in layout.root_conftests]
            + [
                parse(p, "conftest", layout.level_of_conftest(p))
                for p in layout.suite_conftests
            ]
            + [parse(p, "test", "module", collect=True) for p in layout.test_files]
            + [parse(p, "helper", "helper") for p in layout.helper_files]
        )
        self.suite_conftests = [layout.rel(p) for p in layout.suite_conftests]
        self.parse_errors = [
            f"{m.rel}: {m.parse_error}" for m in self.modules if m.parse_error
        ]

    def _firefox_rel(self, path: Path) -> str:
        root = self.opts.firefox_root
        path = path.resolve()
        if root and root.resolve() in path.parents:
            return path.relative_to(root.resolve()).as_posix()
        return str(path)

    def _parse_firefox(self):
        self.ff_modules = [
            parse_module(
                _read(p),
                self._firefox_rel(p),
                kind="conftest",
                origin="firefox",
                level="firefox_root",
            )
            for p in self.opts.firefox_conftests
        ]
        self.site = (
            parse_firefox_sites(self.opts.firefox_sites, self.opts.firefox_root)
            if self.opts.firefox_sites
            else None
        )

    def _parse_environment(self):
        self.env = Environment(self.opts.site_packages)
        self.plugins: dict[str, list[ModuleInfo]] = defaultdict(list)
        for dist in self.env.dists.values():
            for module, path in dist.plugin_files:
                self.plugins[dist.name].append(
                    parse_module(
                        _read(path),
                        f"{dist.name}:{module}",
                        kind="plugin",
                        origin=f"plugin:{dist.name}",
                        level="plugin",
                    )
                )
        files, _ = self.env.pytest_builtin_files()
        self.builtins = [
            parse_module(
                _read(p),
                f"pytest:{p.name}",
                kind="plugin",
                origin="builtin",
                level="builtin",
            )
            for p in files
        ]
        if not files:
            self.notes.append(
                "pytest's own source was not found: built-in fixtures count as missing."
            )
        if self.site:
            pypi = {f.value for f in self.site.pypi}
            self.ff_dists, unknown = self.env.closure(pypi)
            self.ff_import_names = set(self.site.modules) | {
                m for d in self.ff_dists for m in self.env.dists[d].top_level
            }
            if unknown:
                self.notes.append(
                    "Firefox site requirements not installed in the scanned environment, "
                    f"so their own dependencies are unknown: {sorted(unknown)}"
                )
            self.ff_dists |= unknown
        else:
            self.ff_dists = set(self.plugins)
            self.ff_import_names = None
            self.notes.append(
                "No Firefox site file given: assumed every scanned plugin and package "
                "is available in Firefox."
            )

    # Worlds

    def _build_worlds(self):
        tests_dir = PurePosixPath(self.tests_rel)
        above = [tests_dir.parent, *tests_dir.parent.parents]
        self.sf = World(
            "starfox", self.tests_rel, [("dir", d.as_posix()) for d in above]
        )
        ff_keys = [
            ("ext", m.rel)
            for m in sorted(
                self.ff_modules, key=lambda m: -len(PurePosixPath(m.rel).parts)
            )
        ]
        self.ff = World("firefox", self.tests_rel, ff_keys)
        helpers = {_dotted(m.rel): m for m in self.modules if m.kind == "helper"}
        root_rels = {self.layout.rel(p) for p in self.layout.root_conftests}
        for m in self.modules:
            if m.kind == "helper":
                continue
            key = (
                ("dir", PurePosixPath(m.rel).parent.as_posix())
                if m.kind == "conftest"
                else ("module", m.rel)
            )
            worlds = [self.sf] if m.rel in root_rels else [self.sf, self.ff]
            for f in m.fixtures:
                k = ("class", m.rel, f.container) if f.container else key
                for w in worlds:
                    w.add(k, f)
            for f in self._imported_fixtures(m, helpers):
                for w in worlds:
                    w.add(key, f)
        for m in self.ff_modules:
            for f in m.fixtures:
                self.ff.add(("ext", m.rel), f)
        # What Firefox would have to bring along: STARfox root fixtures, nearest
        # conftest first, then plugins Firefox does not install.
        for key in self.sf.root_keys:
            for f in self.sf.layers.get(key, {}).values():
                self.ff.add_carry_over(key, f)
        for dist, mods in self.plugins.items():
            for m in mods:
                for f in m.fixtures:
                    self.sf.add(("plugin", dist), f)
                    if dist in self.ff_dists:
                        self.ff.add(("plugin", dist), f)
                    else:
                        self.ff.add_carry_over(("plugin", dist), f)
        for m in self.builtins:
            for f in m.fixtures:
                self.sf.add(("builtin",), f)
                self.ff.add(("builtin",), f)

    def _imported_fixtures(self, m: ModuleInfo, helpers: dict[str, ModuleInfo]):
        """Fixtures a test module or conftest imports from a helper in the tests dir."""
        pkg = PurePosixPath(m.rel).parent.parts
        for imp in m.imports:
            if imp.kind != "import" or not imp.detail:
                continue
            mod = imp.value
            if mod.startswith("."):
                level = len(mod) - len(mod.lstrip("."))
                base = pkg[: len(pkg) - level + 1] if level else pkg
                mod = ".".join([*base, mod.lstrip(".")]).strip(".")
            helper = helpers.get(mod)
            if not helper:
                continue
            names = set(imp.detail.split(","))
            yield from (f for f in helper.fixtures if f.func_name in names)

    # What the converter asks

    def fixtures_in(self, rel: str) -> list[FixtureDef]:
        return [f for m in self.modules if m.rel == rel for f in m.fixtures]

    def module_facts(self, rel: str) -> list[Finding]:
        return [f for m in self.modules if m.rel == rel for f in m.facts]

    def root_fixture(self, name: str) -> FixtureDef | None:
        """The STARfox root fixture pytest would pick for this name, nearest conftest first."""
        return self.sf.lookup(self.sf.root_keys, name)[0]

    def firefox_twin(self, d: FixtureDef) -> FixtureDef | None:
        """The code-identical Firefox fixture that `d` would shadow after migration."""
        parent = self.ff.parent_of(d)
        if (
            parent
            and parent.origin == "firefox"
            and parent.fingerprint == d.fingerprint
        ):
            return parent
        return None

    def tests_using_after_migration(self, d: FixtureDef) -> int:
        return len(self.ff_res.used_by_tests.get(d.id, ()))

    def missing_requests(self, d: FixtureDef) -> list[str]:
        """Names `d` requests that nothing in the Firefox tree provides."""
        return sorted(
            name
            for name, info in self.ff_res.missing.items()
            if d.id in info["requesters"]
        )

    def cleanup_note(self, d: FixtureDef) -> str | None:
        """Why a kept fixture looks removable; informational only."""
        parent = self.sf.parent_of(d)
        if parent and parent.fingerprint == d.fingerprint:
            return f"code-identical to {parent.file}:{parent.line}, which it shadows"
        used = self.sf_res.used_by_tests.get(d.id) or self.ff_res.used_by_tests.get(
            d.id
        )
        return None if used else "not used by any analysed test"

    @property
    def tests_package(self) -> str | None:
        top = PurePosixPath(self.tests_rel).parts[0]
        return top if top in self.layout.repo_packages else None

    def _helper_starfox_imports(self) -> dict[str, list[str]]:
        """For modules in the tests package, the STARfox-only modules they import."""
        pkg = self.tests_package
        if not pkg:
            return {}
        modules = {_dotted(m.rel): m for m in self.modules}
        direct, deps = {}, {}
        for name, m in modules.items():
            tops = [
                (f.value, f.value.split(".")[0])
                for f in m.imports
                if not f.value.startswith(".")
            ]
            direct[name] = {
                v for v, t in tops if t in self.layout.repo_packages and t != pkg
            }
            deps[name] = {v for v, t in tops if t == pkg and v in modules}
        result = {}
        for name in modules:
            seen, stack, found = set(), [name], set()
            while stack:
                cur = stack.pop()
                if cur in seen:
                    continue
                seen.add(cur)
                found |= direct.get(cur, set())
                stack.extend(deps.get(cur, ()))
            if found:
                result[name] = sorted(found)
        return result

    def _repo_import_reason(self, module: str, symbol: str, where: str) -> str | None:
        top = module.split(".")[0]
        full = f"{module}.{symbol}" if symbol else module
        if module.startswith("."):
            return None
        if self.tests_package and top == self.tests_package:
            via = self.helper_starfox_imports.get(module)
            return (
                f"uses {full}, which imports STARfox-only {via} ({where})"
                if via
                else None
            )
        if top in self.layout.repo_packages:
            return f"uses repo-local {full} ({where})"
        return None

    def starfox_specific_reasons(self, d: FixtureDef) -> list[str]:
        """Uses of STARfox-only code or CLI options, with locations."""
        reasons = []
        for f in d.facts:
            if f.category == "import":
                symbol = f.detail if f.kind == "used" else ""
                if reason := self._repo_import_reason(
                    f.value, symbol, f"{f.file}:{f.line}"
                ):
                    reasons.append(reason)
            elif f.category == "cli_option" and not (
                option_keys(f.value) & self.firefox_options
            ):
                reasons.append(
                    f"reads CLI option {f.value} that Firefox does not define "
                    f"({f.file}:{f.line})"
                )
        return sorted(set(reasons))

    def firefox_lacks_module(self, top: str) -> bool:
        """True when Firefox's mach venv cannot import this top-level module."""
        if top in self.layout.repo_packages:
            return True
        if top in stdlib_modules() or self.ff_import_names is None:
            return False
        return top not in self.ff_import_names

    def suite_tests_need(self, suite: str) -> dict[str, int]:
        """Missing names this suite's tests need after migration, with test counts."""
        need = Counter()
        for t in self.tests:
            if t.suite == suite:
                need.update(self.ff_res.per_test[t.id]["missing"])
        return dict(sorted(need.items()))

    def suite_repo_imports(self, suite: str) -> list[str]:
        """Repo-local modules imported anywhere in this suite."""
        return sorted(
            {
                f.value
                for m in self.modules
                if m.suite == suite
                for f in m.imports
                if f.value.startswith(".")
                or f.value.split(".")[0] in self.layout.repo_packages
            }
        )

    def root_gaps(self) -> list[dict]:
        """Fixtures suite conftests need after migration that Firefox lacks."""
        defs = {
            f.id: f
            for m in self.modules + [m for ms in self.plugins.values() for m in ms]
            for f in m.fixtures
        }
        suite_ids = {
            f.id for rel in self.suite_conftests for f in self.fixtures_in(rel)
        }
        requested, provided = defaultdict(set), defaultdict(set)
        queue, seen = sorted(suite_ids), set()
        while queue:
            rid = queue.pop()
            if rid in seen:
                continue
            seen.add(rid)
            for name, info in self.ff_res.missing.items():
                if rid in info["requesters"]:
                    requested[name].add(rid)
                    provided[name] |= self.ff_res.carried_over.get(name, set())
                    queue += sorted(self.ff_res.carried_over.get(name, set()))
            d = defs.get(rid)
            if d is None or rid in suite_ids:
                continue
            # A fixture Firefox takes on needs every name it declares in Firefox's
            # root too, even where tests override that name.
            for arg in d.args:
                if arg != d.name and not self.firefox_provides(arg):
                    if root := self.root_fixture(arg):
                        requested[arg].add(rid)
                        provided[arg].add(root.id)
                        queue.append(root.id)
        return [
            {
                "name": name,
                "requested_by": sorted(defs[r].name if r in defs else r for r in reqs),
                "starfox_provides": sorted(provided[name]) or ["nothing"],
            }
            for name, reqs in sorted(requested.items())
        ]

    def firefox_provides(self, name: str) -> FixtureDef | None:
        """Firefox's own definition of a name: its conftests, plugins or pytest."""
        return self.ff.lookup(self.ff.root_keys + self.ff.plugin_keys, name)[0]
