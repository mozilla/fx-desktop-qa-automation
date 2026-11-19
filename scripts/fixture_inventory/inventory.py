"""Build the inventory: discover, parse, resolve in both worlds, classify, aggregate."""

import datetime
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path, PurePosixPath
from types import SimpleNamespace

from . import __version__
from .classify import (
    CATEGORY_LABELS,
    Context,
    classify,
    locality_of,
    option_keys,
    starfox_specific_reasons,
)
from .config import discover_configs, read_config
from .discovery import discover
from .environment import Environment, parse_firefox_sites, stdlib_modules
from .models import Finding, FixtureDef, ModuleInfo
from .parser import parse_module, url_host
from .resolver import World

SCHEMA_VERSION = 1

CONFIRMED = [
    "Fixture, hook, test, import, env var, asset and CLI option findings come from "
    "parsing source with ast; each has a file and line.",
    "Code identity between same-name fixtures compares normalized code, including "
    "helpers and constants from the same module.",
]
ASSUMPTIONS = [
    "Fixture resolution follows pytest's rules as modelled here (class, module, "
    "conftests up to the tests dir, root conftests, plugins, built-ins). The tool "
    "does not ask pytest.",
    "The 'firefox' world swaps the STARfox root conftests for the given Firefox "
    "conftests and keeps suite conftests and test files unchanged.",
    "Packages and plugins available in Firefox are the given mach site files plus "
    "their requirements, as recorded in the scanned environment's metadata. "
    "Installed versions there may differ from what mach installs.",
    "'Code-identical' means the same code, not proven same behaviour: imported "
    "symbols are compared by name only.",
]
LIMITATIONS = [
    "Fixtures added at runtime (pytest_plugins strings, plugin objects registered "
    "in hooks, pytest_generate_tests, request.getfixturevalue with a variable) are "
    "reported, not resolved.",
    "Fixtures imported into a test module are only followed when they come from a "
    "module inside the tests dir.",
    "Plugin fixtures are only found in a plugin's entry-point module, not in modules "
    "it imports.",
    "Asset detection is pattern-based: it can miss paths built from variables and can "
    "flag strings that only look like paths.",
    "Markers registered by plugins or conftests at runtime with non-literal strings "
    "are not seen.",
]


@dataclass
class Options:
    repo: Path
    tests_dir: str = "tests"
    exclude_suites: tuple[str, ...] = ()
    firefox_conftests: list[Path] = field(default_factory=list)
    firefox_root: Path | None = None
    firefox_sites: list[Path] = field(default_factory=list)
    firefox_configs: list[Path] = field(default_factory=list)
    site_packages: list[Path] | None = None


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _loc(f: Finding) -> str:
    return f"{f.file}:{f.line}"


def _fixture_dict(d: FixtureDef) -> dict:
    data = asdict(d)
    data["id"] = d.id
    data.pop("facts")
    return data


def _finding_dict(f: Finding, owner: str | None = None) -> dict:
    data = asdict(f)
    if owner:
        data["owner"] = owner
    return data


class Inventory:
    def __init__(self, opts: Options):
        self.opts = opts
        self.notes: list[str] = []

    # Parsing

    def _parse_repo(self):
        self.configs = discover_configs(self.opts.repo)
        root_cfg = next((c for c in self.configs if "/" not in c.file), None)

        def setting(key, default):
            return (root_cfg.option_list(key) if root_cfg else ()) or default

        python_files = setting("python_files", ("test_*.py", "*_test.py"))
        self.layout = layout = discover(
            self.opts.repo, self.opts.tests_dir, python_files, self.opts.exclude_suites
        )
        self.tests_rel = layout.rel(layout.tests_dir)
        common = {
            "repo_entries": layout.repo_entries,
            "python_functions": setting("python_functions", ("test",)),
            "python_classes": setting("python_classes", ("Test",)),
        }

        def parse(path, kind, level, collect=False):
            return parse_module(
                _read(path),
                layout.rel(path),
                kind=kind,
                origin="starfox",
                level=level,
                suite=layout.suite_of(path),
                collect_tests=collect,
                **common,
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
        self.outside = [
            parse(p, "conftest", "outside") for p in layout.outside_conftests
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
        self.ff_configs = [
            c
            for p in self.opts.firefox_configs
            if (c := read_config(p, self._firefox_rel(p)))
        ]
        self.site = (
            parse_firefox_sites(self.opts.firefox_sites, self.opts.firefox_root)
            if self.opts.firefox_sites
            else None
        )
        if not self.opts.firefox_conftests:
            self.notes.append(
                "No Firefox conftest given: every root fixture counts as missing."
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
        files, self.builtin_source = self.env.pytest_builtin_files()
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
                "pytest's own source was not found: built-in fixtures are unknown."
            )
        if self.site:
            pypi = {f.value for f in self.site.pypi}
            self.ff_dists, unknown = self.env.closure(pypi)
            self.ff_import_names = set(self.site.modules) | {
                m for d in self.ff_dists for m in self.env.dists[d].top_level
            }
            if unknown:
                self.notes.append(
                    "Firefox site requirements not installed in the scanned environment, so "
                    f"their own dependencies are unknown: {sorted(unknown)}"
                )
            self.ff_dists |= unknown
        else:
            self.ff_dists = set(self.plugins)
            self.ff_import_names = None
            self.notes.append(
                "No Firefox site file given: assumed every scanned plugin is available in Firefox."
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
        helpers = {
            ".".join(PurePosixPath(m.rel).with_suffix("").parts): m
            for m in self.modules
            if m.kind == "helper"
        }
        self.imported_helpers: set[str] = set()
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
                self.imported_helpers.add(f.id)
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

    # Assembly

    def build(self) -> dict:
        self._parse_repo()
        self._parse_firefox()
        self._parse_environment()
        self._build_worlds()
        self.tests = [t for m in self.modules for t in m.tests]
        self.sf_res = self.sf.resolve(self.tests)
        self.ff_res = self.ff.resolve(self.tests)
        self.starfox_defs = [f for m in self.modules for f in m.fixtures]
        all_defs = (
            self.starfox_defs
            + [f for m in self.ff_modules for f in m.fixtures]
            + [f for ms in self.plugins.values() for m in ms for f in m.fixtures]
            + [f for m in self.builtins for f in m.fixtures]
        )
        self.defs_by_id = {f.id: f for f in all_defs}
        shadowed_by = defaultdict(list)
        for d in self.starfox_defs:
            if parent := self.sf.parent_of(d):
                shadowed_by[parent.id].append(d)
        self.shadowed_by = shadowed_by
        self.ctx = Context(
            sf=self.sf,
            ff=self.ff,
            sf_res=self.sf_res,
            ff_res=self.ff_res,
            defs_by_id=self.defs_by_id,
            shadowed_by=shadowed_by,
            repo_packages=self.layout.repo_packages,
            firefox_options=self._firefox_options(),
            imported_helpers=self.imported_helpers,
            tests_package=self.tests_package,
            helper_starfox_imports=self._helper_starfox_imports(),
            starfox_options={
                k
                for m in self.modules
                for f in m.options_defined
                for k in option_keys(f.value)
            },
        )
        fixtures = self._fixtures()
        return {
            "meta": self._meta(),
            "summary": self._summary(fixtures),
            "files": self._files(),
            "fixtures": fixtures,
            "missing_after_migration": self._missing(),
            "unresolved_references": self._unresolved_refs(),
            "optional_requests_missing_after_migration": {
                name: sorted(reqs)
                for name, reqs in sorted(self.ff_res.optional_missing.items())
            },
            "duplicates": self._duplicates(),
            "overrides": self._overrides(),
            "hooks": self._hooks(),
            "config": self._config(),
            "imports": self._imports(),
            "facts": self._facts(),
            "suites": self._suites(fixtures),
            "tests": self._tests(),
            "graph": self._graph(),
        }

    @property
    def tests_package(self) -> str | None:
        top = PurePosixPath(self.tests_rel).parts[0]
        return top if top in self.layout.repo_packages else None

    @staticmethod
    def _dotted(rel: str) -> str:
        parts = PurePosixPath(rel).with_suffix("").parts
        return ".".join(parts[:-1] if parts[-1] == "__init__" else parts)

    def _helper_starfox_imports(self) -> dict[str, list[str]]:
        """For modules in the tests package, the STARfox-only modules they import."""
        pkg = self.tests_package
        if not pkg:
            return {}
        modules = {self._dotted(m.rel): m for m in self.modules}
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

    def _firefox_options(self) -> set[str]:
        sources = list(self.ff_modules) + list(self.builtins)
        sources += [
            m for d, ms in self.plugins.items() if d in self.ff_dists for m in ms
        ]
        return {
            k for m in sources for f in m.options_defined for k in option_keys(f.value)
        }

    def _meta(self) -> dict:
        return {
            "tool": f"fixture_inventory {__version__}",
            "schema_version": SCHEMA_VERSION,
            "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(
                timespec="seconds"
            ),
            "inputs": {
                "repo": str(self.opts.repo),
                "tests_dir": self.tests_rel,
                "excluded_suites": list(self.opts.exclude_suites),
                "firefox_conftests": [m.rel for m in self.ff_modules],
                "firefox_sites": self.site.files if self.site else [],
                "firefox_configs": [c.file for c in self.ff_configs],
                "site_packages": [str(p) for p in self.opts.site_packages or []]
                or "current interpreter",
                "pytest_builtins": self.builtin_source,
            },
            "worlds": {
                "starfox": "STARfox as it is today",
                "firefox": "after migration: suite conftests and tests moved under the Firefox conftest(s)",
            },
            "categories": CATEGORY_LABELS,
            "confirmed": CONFIRMED,
            "assumptions": ASSUMPTIONS,
            "limitations": LIMITATIONS,
            "notes": self.notes,
        }

    def _files(self) -> dict:
        return {
            "root_conftests": [self.layout.rel(p) for p in self.layout.root_conftests],
            "suite_conftests": [
                self.layout.rel(p) for p in self.layout.suite_conftests
            ],
            "outside_tests_dir_conftests": [
                self.layout.rel(p) for p in self.layout.outside_conftests
            ],
            "test_files": len(self.layout.test_files),
            "helper_files": [self.layout.rel(p) for p in self.layout.helper_files],
            "excluded_files": len(self.layout.excluded_files),
            "tests": len(self.tests),
            "parse_errors": [
                {"file": m.rel, "error": m.parse_error}
                for m in self.modules + self.ff_modules
                if m.parse_error
            ],
            "pytest_plugins_declarations": [
                _finding_dict(f) for m in self.modules for f in m.pytest_plugins
            ],
            "modules_with_pytest_generate_tests": [
                m.rel for m in self.modules if m.generates_tests
            ],
        }

    def _fixtures(self) -> list[dict]:
        out = []
        for d in self.starfox_defs:
            used_sf = self.sf_res.used_by_tests.get(d.id, set())
            consumers = self.sf_res.consumers.get(d.id, set())
            parent = self.sf.parent_of(d)
            item = _fixture_dict(d)
            if d.id in self.imported_helpers:
                item["level"] = "imported_helper"
            item.update(classify(d, self.ctx))
            item.update(
                {
                    "tests_using_starfox": len(used_sf),
                    "tests_using_after_migration": len(
                        self.ff_res.used_by_tests.get(d.id, set())
                    ),
                    "suites_using": sorted(
                        {self._suite_of_test(t) or "-" for t in used_sf}
                    ),
                    "consumer_fixtures": sorted(
                        c for c in consumers if c in self.defs_by_id
                    ),
                    "tests_requesting_directly": len(
                        [c for c in consumers if c not in self.defs_by_id]
                    ),
                    "inheritance": locality_of(d, used_sf),
                    "shadows": parent.id if parent else None,
                    "shadowed_by": sorted(o.id for o in self.shadowed_by.get(d.id, [])),
                    "facts": [_finding_dict(f) for f in self._dedupe(d.facts)],
                }
            )
            out.append(item)
        return out

    @staticmethod
    def _dedupe(findings):
        seen, out = set(), []
        for f in findings:
            key = (f.category, f.kind, f.value, f.file, f.line)
            if key not in seen:
                seen.add(key)
                out.append(f)
        return out

    def _suite_of_test(self, test_id: str) -> str | None:
        return self.layout.suite_of(self.layout.repo / test_id.split("::")[0])

    def _summary(self, fixtures: list[dict]) -> dict:
        by_level = defaultdict(Counter)
        for f in fixtures:
            by_level[f["level"]][f["category"]] += 1
        return {
            "tests": len(self.tests),
            "fixture_definitions": len(fixtures),
            "categories_by_level": {k: dict(v) for k, v in sorted(by_level.items())},
            "tests_missing_fixtures_after_migration": sum(
                1 for t in self.ff_res.per_test.values() if t["missing"]
            ),
            "missing_names_after_migration": len(self.ff_res.missing),
            "unresolved_names_in_starfox": len(self.sf_res.missing),
        }

    def _missing(self) -> list[dict]:
        out = []
        carried = {i for ids in self.ff_res.carried_over.values() for i in ids}
        for name, info in sorted(
            self.ff_res.missing.items(), key=lambda kv: -len(kv[1]["tests"])
        ):
            providers = sorted(self.ff_res.carried_over.get(name, set()))
            if name in self.sf_res.missing:
                providers.append("nothing")
            origins = sorted(
                {self.defs_by_id[p].origin for p in providers if p in self.defs_by_id}
            )
            fixture_requesters = [r for r in info["requesters"] if r in self.defs_by_id]
            out.append(
                {
                    "name": name,
                    "tests": len(info["tests"]),
                    "suites": sorted(
                        {self._suite_of_test(t) or "-" for t in info["tests"]}
                    ),
                    "requested_by_fixtures": sorted(fixture_requesters),
                    "requested_directly_by_tests": len(
                        [r for r in info["requesters"] if r not in self.defs_by_id]
                    ),
                    "only_needed_through_other_missing_fixtures": all(
                        r in carried for r in info["requesters"]
                    ),
                    "starfox_providers": providers,
                    "starfox_provider_origins": origins,
                    "also_missing_in_starfox": name in self.sf_res.missing,
                }
            )
        return out

    def _unresolved_refs(self) -> list[dict]:
        generated = {m.rel for m in self.modules if m.generates_tests}
        out = []
        for name, info in sorted(self.sf_res.missing.items()):
            files = sorted({t.split("::")[0] for t in info["tests"]})
            out.append(
                {
                    "name": name,
                    "tests": len(info["tests"]),
                    "requesters": sorted(info["requesters"])[:20],
                    "files": files[:20],
                    "possibly_generated": bool(set(files) & generated),
                }
            )
        return out

    def _duplicates(self) -> list[dict]:
        groups = defaultdict(list)
        for d in self.starfox_defs:
            if d.level in ("root", "suite", "tests_root"):
                groups[d.name].append(d)
        out = []
        for name, defs in sorted(groups.items()):
            if len(defs) < 2:
                continue
            by_fp = defaultdict(list)
            for d in defs:
                by_fp[d.fingerprint].append(f"{d.file}:{d.line}")
            out.append(
                {
                    "name": name,
                    "definitions": len(defs),
                    "distinct_implementations": len(by_fp),
                    "implementations": [
                        {"fingerprint": fp, "locations": locs}
                        for fp, locs in by_fp.items()
                    ],
                }
            )
        return out

    def _overrides(self) -> list[dict]:
        counts = defaultdict(list)
        for d in self.starfox_defs:
            if d.level in ("module", "class"):
                counts[d.name].append(d.file)
        return [
            {
                "name": n,
                "test_files": len(set(files)),
                "shadows": sorted(
                    {
                        self.sf.parent_of(d).id
                        for d in self.starfox_defs
                        if d.name == n
                        and d.level in ("module", "class")
                        and self.sf.parent_of(d)
                    }
                ),
            }
            for n, files in sorted(counts.items(), key=lambda kv: -len(kv[1]))
        ]

    def _hooks(self) -> list[dict]:
        ff_hooks = defaultdict(list)
        for m in self.ff_modules:
            for h in m.hooks:
                ff_hooks[h.name].append(f"{h.file}:{h.line}")
        out = []
        for m in self.modules:
            for h in m.hooks:
                facts = self._dedupe(h.facts)
                out.append(
                    {
                        "name": h.name,
                        "file": h.file,
                        "line": h.line,
                        "module_kind": m.kind,
                        "firefox_defines_same_hook": ff_hooks.get(h.name, []),
                        "fixtures_referenced": sorted(
                            {f.value for f in facts if f.category == "fixture_request"}
                        ),
                        "env_vars": sorted(
                            {f.value for f in facts if f.category == "env_var"}
                        ),
                        "cli_options": sorted(
                            {f.value for f in facts if f.category == "cli_option"}
                        ),
                        "commands": sorted(
                            {f.value for f in facts if f.category == "command"}
                        ),
                        "starfox_specific_reasons": starfox_specific_reasons(
                            SimpleNamespace(facts=facts), self.ctx
                        ),
                        "facts": [_finding_dict(f) for f in facts],
                    }
                )
        for m in self.ff_modules:
            for h in m.hooks:
                out.append(
                    {
                        "name": h.name,
                        "file": h.file,
                        "line": h.line,
                        "module_kind": "firefox_conftest",
                    }
                )
        return out

    def _options_map(self) -> dict[str, str]:
        providers = {}
        for m in self.modules:
            for f in m.options_defined:
                providers.setdefault(f.value, f"STARfox {f.file}:{f.line}")
        for dist, ms in self.plugins.items():
            for m in ms:
                for f in m.options_defined:
                    providers.setdefault(f.value, f"plugin {dist}")
        for m in self.builtins:
            for f in m.options_defined:
                providers.setdefault(f.value, "pytest")
        for m in self.ff_modules:
            for f in m.options_defined:
                providers.setdefault(f.value, f"Firefox {f.file}:{f.line}")
        return providers

    @staticmethod
    def _addopts_flags(addopts: list[str], providers: dict[str, str]) -> list[str]:
        """Return the flags in addopts, splitting combined short flags like -vs."""
        flags = []
        for token in addopts:
            if not token.startswith("-"):
                continue
            flag = token.split("=", 1)[0]
            short = not flag.startswith("--") and len(flag) > 2 and flag[1:].isalpha()
            if short and flag not in providers:
                flags.extend(f"-{ch}" for ch in flag[1:])
            else:
                flags.append(flag)
        return flags

    def _config(self) -> dict:
        providers = self._options_map()
        ff_opts = self.ctx.firefox_options
        configs = []
        for c in self.configs:
            flags = []
            for flag in self._addopts_flags(c.addopts, providers):
                flags.append(
                    {
                        "flag": flag,
                        "provider": providers.get(flag, "unknown"),
                        "available_in_firefox": bool(option_keys(flag) & ff_opts),
                    }
                )
            configs.append(
                {
                    "file": c.file,
                    "markers": c.markers,
                    "addopts": c.addopts,
                    "addopts_flags": flags,
                    "other_settings": c.options,
                }
            )
        return {
            "starfox": configs,
            "firefox": [asdict(c) for c in self.ff_configs],
            "markers": self._markers(),
        }

    def _markers(self) -> list[dict]:
        builtin = {f.value for m in self.builtins for f in m.markers_registered}
        plugin_marks = {
            f.value: d
            for d, ms in self.plugins.items()
            for m in ms
            for f in m.markers_registered
        }
        sf_registered = {mk for c in self.configs for mk in c.markers} | {
            f.value for m in self.modules for f in m.markers_registered
        }
        ff_registered = (
            {mk for c in self.ff_configs for mk in c.markers}
            | {f.value for m in self.ff_modules for f in m.markers_registered}
            | {mk for mk, d in plugin_marks.items() if d in self.ff_dists}
        )
        used = defaultdict(list)
        for t in self.tests:
            for f in t.markers:
                used[f.value.split("(")[0]].append(f)
        out = []
        for name, findings in sorted(used.items()):
            locations = sorted({_loc(f) for f in findings})
            out.append(
                {
                    "name": name,
                    "tests": len(findings),
                    "builtin": name in builtin,
                    "provided_by_plugin": plugin_marks.get(name),
                    "registered_in_starfox": name in sf_registered
                    or name in builtin
                    or name in plugin_marks,
                    "registered_in_firefox": name in ff_registered or name in builtin,
                    "locations": locations[:10],
                }
            )
        return out

    def _categorize_import(self, module: str) -> dict:
        top = module.lstrip(".").split(".")[0]
        if module.startswith(".") or top in self.layout.repo_packages:
            category = "repo_local"
        elif top in stdlib_modules():
            category = "stdlib"
        elif top in self.env.module_to_dist:
            category = "third_party"
        else:
            category = "unknown"
        dist = None if category == "repo_local" else self.env.module_to_dist.get(top)
        available = None
        if category == "stdlib":
            available = True
        elif category == "repo_local":
            available = False
        elif self.ff_import_names is not None:
            available = top in self.ff_import_names
        return {
            "category": category,
            "distribution": dist,
            "available_in_firefox": available,
        }

    def _imports(self) -> list[dict]:
        by_top = defaultdict(list)
        for m in self.modules:
            for f in m.imports:
                by_top[
                    f.value if f.value.startswith(".") else f.value.split(".")[0]
                ].append((m, f))
        out = []
        for top, items in sorted(by_top.items()):
            info = self._categorize_import(top)
            out.append(
                {
                    "module": top,
                    **info,
                    "files": len({m.rel for m, _ in items}),
                    "suites": sorted({m.suite or "-" for m, _ in items}),
                    "submodules": sorted({f.value for _, f in items}),
                    "locations": sorted({_loc(f) for _, f in items})[:25],
                }
            )
        return out

    def _all_facts(self):
        """Yield (owner, finding) for every fact, deduplicated by location."""
        seen = set()
        sources = []
        for m in self.modules:
            sources += [(m.rel, f) for f in m.facts]
            sources += [(t.id, f) for t in m.tests for f in t.facts]
            sources += [(d.id, f) for d in m.fixtures for f in d.facts]
            sources += [(f"{h.file}::{h.name}", f) for h in m.hooks for f in h.facts]
        for owner, f in sources:
            key = (f.category, f.kind, f.value, f.file, f.line)
            if key in seen or f.category in ("import", "fixture_request"):
                continue
            seen.add(key)
            yield owner, f

    def _facts(self) -> dict:
        out = defaultdict(list)
        for owner, f in self._all_facts():
            out[f.category].append(_finding_dict(f, owner))
        return dict(out)

    def _suites(self, fixtures: list[dict]) -> dict:
        suites = defaultdict(
            lambda: {
                "tests": 0,
                "tests_with_missing_fixtures": 0,
                "missing_after_migration": Counter(),
                "fixture_categories": Counter(),
                "repo_paths": 0,
                "urls": set(),
                "env_vars": set(),
                "repo_local_imports": set(),
                "unregistered_markers_in_firefox": set(),
            }
        )
        for t in self.tests:
            s = suites[t.suite or "-"]
            s["tests"] += 1
            missing = self.ff_res.per_test[t.id]["missing"]
            s["tests_with_missing_fixtures"] += bool(missing)
            s["missing_after_migration"].update(missing)
        for f in fixtures:
            if f["suite"]:
                suites[f["suite"]]["fixture_categories"][f["category"]] += 1
        for owner, f in self._all_facts():
            suite = self.layout.suite_of(self.layout.repo / f.file)
            if not suite:
                continue
            s = suites[suite]
            if f.category == "asset" and f.kind == "repo_path":
                s["repo_paths"] += 1
            elif f.category == "asset" and f.kind == "url":
                s["urls"].add(url_host(f.value))
            elif f.category == "env_var":
                s["env_vars"].add(f.value)
        for m in self.modules:
            for f in m.imports:
                if (
                    m.suite
                    and self._categorize_import(f.value)["category"] == "repo_local"
                ):
                    suites[m.suite]["repo_local_imports"].add(f.value)
        unregistered = {
            mk["name"] for mk in self._markers() if not mk["registered_in_firefox"]
        }
        for t in self.tests:
            for f in t.markers:
                if f.value in unregistered:
                    suites[t.suite or "-"]["unregistered_markers_in_firefox"].add(
                        f.value
                    )
        return {
            name: {
                k: (
                    dict(v)
                    if isinstance(v, Counter)
                    else sorted(v)
                    if isinstance(v, set)
                    else v
                )
                for k, v in data.items()
            }
            for name, data in sorted(suites.items())
        }

    def _tests(self) -> list[dict]:
        return [
            {
                "id": t.id,
                "line": t.line,
                "suite": t.suite,
                "markers": sorted({f.value for f in t.markers}),
                "fixtures_starfox": self.sf_res.per_test[t.id]["fixtures"],
                "fixtures_after_migration": self.ff_res.per_test[t.id]["fixtures"],
                "missing_after_migration": self.ff_res.per_test[t.id]["missing"],
                "carried_over_after_migration": self.ff_res.per_test[t.id][
                    "carried_over"
                ],
            }
            for t in self.tests
        ]

    def _graph(self) -> dict:
        graphs = {}
        for res in (self.sf_res, self.ff_res):
            edges = defaultdict(int)
            test_requests = Counter()
            for (src, dst), n in res.edges.items():
                if src in self.defs_by_id:
                    edges[(src, dst)] += n
                else:
                    test_requests[dst] += 1
            node_ids = {i for e in edges for i in e} | set(test_requests)
            graphs[res.name] = {
                "nodes": [
                    {
                        "id": i,
                        "name": self.defs_by_id[i].name,
                        "origin": self.defs_by_id[i].origin,
                        "level": self.defs_by_id[i].level,
                        "requested_directly_by_tests": test_requests.get(i, 0),
                    }
                    for i in sorted(node_ids)
                ],
                "edges": [
                    {"from": s, "to": d, "test_closures": n}
                    for (s, d), n in sorted(edges.items())
                ],
                "missing": sorted(res.missing),
            }
        return graphs
