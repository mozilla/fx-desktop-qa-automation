"""Write the inventory as JSON, Markdown and Graphviz DOT."""

import json
from collections import Counter, defaultdict
from pathlib import Path

from .parser import url_host

CONFTEST_LEVELS = ("root", "suite", "tests_root")
GRAPH_LEVELS = CONFTEST_LEVELS + ("firefox_root", "plugin", "builtin")
COLORS = {
    "available_in_firefox": "#b7e1cd",
    "missing_required": "#f4c7c3",
    "potentially_redundant": "#e0e0e0",
    "consumer_removed": "#d9d2e9",
    "starfox_specific": "#fce8b2",
    "unresolved": "#f9cb9c",
    "suite_local": "#c9daf8",
}


def _cell(value) -> str:
    if isinstance(value, (list, tuple, set)):
        value = ", ".join(str(v) for v in value)
    return (
        str(value if value not in (None, "") else "-")
        .replace("|", "\\|")
        .replace("\n", " ")
    )


def _table(headers: list[str], rows: list[list], limit: int | None = None) -> list[str]:
    if not rows:
        return ["_None._", ""]
    shown = rows[:limit] if limit else rows
    out = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    out += ["| " + " | ".join(_cell(c) for c in r) + " |" for r in shown]
    if limit and len(rows) > limit:
        out.append(f"\n_{len(rows) - limit} more rows in the JSON report._")
    return out + [""]


def _short(items, n=4) -> str:
    items = list(items)
    return ", ".join(map(str, items[:n])) + (
        f" (+{len(items) - n})" if len(items) > n else ""
    )


def _eq(fx: dict) -> str:
    eq = fx.get("firefox_equivalent")
    if not eq:
        return "none"
    status = {
        "code_identical": "code-identical",
        "same_name_code_differs": "same name, code differs",
        "provided_by_plugin": f"plugin ({eq.get('provider')})",
    }[eq["status"]]
    return f"{status}: {eq['file']}:{eq['line']}"


def write_json(inv: dict, path: Path):
    path.write_text(
        json.dumps(inv, indent=2, sort_keys=False, default=sorted) + "\n",
        encoding="utf-8",
    )


def write_dot(inv: dict, world: str, path: Path):
    categories = {f["id"]: f["category"] for f in inv["fixtures"]}
    graph = inv["graph"][world]
    keep = {n["id"]: n for n in graph["nodes"] if n["level"] in GRAPH_LEVELS}
    lines = [
        f'digraph "{world}" {{',
        "  rankdir=LR;",
        "  node [shape=box, style=filled, fontsize=10];",
    ]
    for nid, n in sorted(keep.items()):
        color = COLORS.get(categories.get(nid), "#ffffff")
        label = f"{n['name']}\\n{nid.rsplit('::', 1)[0]}"
        lines.append(f'  "{nid}" [label="{label}", fillcolor="{color}"];')
    for e in graph["edges"]:
        if e["from"] in keep and e["to"] in keep:
            lines.append(
                f'  "{e["from"]}" -> "{e["to"]}" [label="{e["test_closures"]}"];'
            )
    for name in graph["missing"]:
        lines.append(
            f'  "missing:{name}" [label="{name}\\n(missing)", shape=ellipse, fillcolor="#ea9999"];'
        )
    lines.append("}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_markdown(inv: dict, path: Path):
    meta, fixtures = inv["meta"], inv["fixtures"]
    md: list[str] = [f"# Fixture inventory: `{meta['inputs']['repo']}`", ""]
    md += [
        f"Generated {meta['generated_at']} by {meta['tool']}. Full data: `inventory.json`.",
        "",
    ]
    md += _inputs(meta)
    md += _how_to_read(meta)
    md += _summary(inv)
    md += _missing(inv)
    md += _root(fixtures)
    md += _by_category(fixtures)
    md += _blocked(fixtures)
    md += _duplicates(inv)
    md += _hooks(inv)
    md += _config(inv)
    md += _imports(inv)
    md += _facts(inv)
    md += _suites(inv)
    md += _unresolved_refs(inv)
    path.write_text("\n".join(md) + "\n", encoding="utf-8")


def _inputs(meta):
    i = meta["inputs"]
    rows = [
        [k, v if not isinstance(v, list) else (_short(v, 6) if v else "-")]
        for k, v in i.items()
    ]
    return ["## Inputs", ""] + _table(["Input", "Value"], rows)


def _how_to_read(meta):
    md = ["## How to read this", ""]
    md += [f"- **{k}** world: {v}." for k, v in meta["worlds"].items()]
    md += ["", "Categories:", ""] + [
        f"- `{k}`: {v}" for k, v in meta["categories"].items()
    ]
    for title, key in (
        ("Confirmed", "confirmed"),
        ("Assumptions", "assumptions"),
        ("Limitations", "limitations"),
        ("Notes from this run", "notes"),
    ):
        if meta[key]:
            md += ["", f"**{title}**", ""] + [f"- {x}" for x in meta[key]]
    return md + [""]


def _summary(inv):
    s = inv["summary"]
    md = ["## Summary", ""]
    md += [
        f"- Tests analysed: {s['tests']} in {inv['files']['test_files']} files.",
        f"- Fixture definitions: {s['fixture_definitions']}.",
        f"- Tests that would miss at least one fixture after migration: "
        f"{s['tests_missing_fixtures_after_migration']} "
        f"({s['missing_names_after_migration']} distinct names).",
        f"- Names nothing provides even in STARfox: {s['unresolved_names_in_starfox']}.",
        "",
    ]
    cats = list(inv["meta"]["categories"])
    rows = [
        [level] + [counts.get(c, 0) for c in cats]
        for level, counts in s["categories_by_level"].items()
    ]
    return md + _table(["Level"] + cats, rows)


def _missing(inv):
    md = [
        "## Missing after migration",
        "",
        "Names that tests would request, through the closure, with no provider in the "
        "Firefox world.",
        "",
    ]
    rows = [
        [
            m["name"],
            m["tests"],
            _short(m["suites"]),
            _short(m["starfox_providers"], 2),
            _short(m["requested_by_fixtures"], 3),
            m["requested_directly_by_tests"],
            "yes" if m["also_missing_in_starfox"] else "no",
        ]
        for m in inv["missing_after_migration"]
    ]
    return md + _table(
        [
            "Fixture",
            "Tests",
            "Suites",
            "STARfox provider",
            "Requested by fixtures",
            "Direct test requests",
            "Also missing in STARfox",
        ],
        rows,
    )


def _root(fixtures):
    md = ["## Root conftest fixtures", ""]
    rows = [
        [
            f"`{f['name']}`",
            f"{f['file']}:{f['line']}",
            f["scope"],
            "yes" if f["autouse"] else "",
            _short(f["args"], 5),
            f["category"],
            _short(f["reasons"], 1),
            _eq(f),
            f["tests_using_starfox"],
            f["tests_using_after_migration"],
        ]
        for f in fixtures
        if f["level"] == "root"
    ]
    return md + _table(
        [
            "Fixture",
            "Defined",
            "Scope",
            "Autouse",
            "Requests",
            "Category",
            "Why",
            "Firefox",
            "Tests (STARfox)",
            "Tests (after)",
        ],
        rows,
    )


def _by_category(fixtures):
    md = []
    for cat, title in (
        ("starfox_specific", "STARfox-specific fixtures"),
        ("unresolved", "Fixtures needing manual investigation"),
        ("potentially_redundant", "Potentially redundant suite and test fixtures"),
    ):
        rows = [
            [
                f"`{f['name']}`",
                f"{f['file']}:{f['line']}",
                f["level"],
                _short(f["reasons"] + f["starfox_specific_reasons"], 2),
                f["tests_using_starfox"],
            ]
            for f in fixtures
            if f["category"] == cat
            and not (cat == "potentially_redundant" and f["level"] == "root")
        ]
        md += [f"## {title}", ""] + _table(
            ["Fixture", "Defined", "Level", "Why", "Tests"], rows, 40
        )
    return md + _consumer_removed(fixtures)


def _consumer_removed(fixtures):
    """Group by name and reason: many test files override the same fixture."""
    groups = defaultdict(list)
    for f in fixtures:
        if f["category"] == "consumer_removed":
            groups[(f["name"], f["reasons"][0])].append(f)
    rows = [
        [
            f"`{name}`",
            len(items),
            _short(sorted({f["level"] for f in items})),
            reason,
            _short([f"{f['file']}:{f['line']}" for f in items], 2),
        ]
        for (name, reason), items in sorted(groups.items(), key=lambda kv: -len(kv[1]))
    ]
    return [
        "## Fixtures whose consumers disappear after migration",
        "",
        "Used in STARfox, but only by fixtures that do not exist after migration. "
        "Not dead code: keep them if Firefox's replacement takes over the behaviour.",
        "",
    ] + _table(["Fixture", "Definitions", "Levels", "Why", "Examples"], rows, 40)


def _blocked(fixtures):
    rows = [
        [
            f"`{f['name']}`",
            f"{f['file']}:{f['line']}",
            _short(f["blocked_after_migration_by"], 5),
        ]
        for f in fixtures
        if f["level"] != "root" and f["blocked_after_migration_by"]
    ]
    return ["## Suite and test fixtures blocked after migration", ""] + _table(
        ["Fixture", "Defined", "Requests missing"], rows, 60
    )


def _duplicates(inv):
    md = [
        "## Same name in more than one conftest",
        "",
        "Different implementations must not be merged without checking each one.",
        "",
    ]
    rows = [
        [
            f"`{d['name']}`",
            d["definitions"],
            d["distinct_implementations"],
            "; ".join(_short(i["locations"], 3) for i in d["implementations"]),
        ]
        for d in sorted(
            inv["duplicates"], key=lambda d: (-d["distinct_implementations"], d["name"])
        )
    ]
    md += _table(
        ["Fixture", "Definitions", "Distinct code", "Locations by implementation"], rows
    )
    rows = [
        [f"`{o['name']}`", o["test_files"], _short(o["shadows"], 2)]
        for o in inv["overrides"]
    ]
    return (
        md
        + ["### Overridden in test files", ""]
        + _table(["Fixture", "Test files", "Overrides"], rows, 30)
    )


def _hooks(inv):
    rows = [
        [
            f"`{h['name']}`",
            f"{h['file']}:{h['line']}",
            _short(h.get("firefox_defines_same_hook") or [], 2),
            _short(h.get("fixtures_referenced", [])),
            _short(h.get("env_vars", [])),
            _short(h.get("cli_options", [])),
            _short(h.get("commands", [])),
            _short(
                sorted(
                    {f["value"] for f in h.get("facts", []) if f["kind"] == "repo_path"}
                ),
                3,
            ),
            _short(h.get("starfox_specific_reasons", []), 2),
        ]
        for h in inv["hooks"]
    ]
    return ["## Pytest hooks", ""] + _table(
        [
            "Hook",
            "Defined",
            "Firefox same hook",
            "Fixtures read",
            "Env vars",
            "CLI options",
            "Commands",
            "Repo paths",
            "STARfox-specific",
        ],
        rows,
    )


def _config(inv):
    md = ["## Pytest configuration", ""]
    for c in inv["config"]["starfox"]:
        rows = [
            [f["flag"], f["provider"], "yes" if f["available_in_firefox"] else "no"]
            for f in c["addopts_flags"]
        ]
        md += [f"### `{c['file']}`", "", f"Markers: {_short(c['markers'], 12)}", ""]
        md += _table(["addopts flag", "Provided by", "Available in Firefox"], rows)
    rows = [
        [
            f"`{m['name']}`",
            m["tests"],
            "builtin" if m["builtin"] else (m["provided_by_plugin"] or "config"),
            "yes" if m["registered_in_starfox"] else "no",
            "yes" if m["registered_in_firefox"] else "no",
            _short(m["locations"], 2),
        ]
        for m in inv["config"]["markers"]
    ]
    return (
        md
        + ["### Markers used by tests", ""]
        + _table(
            [
                "Marker",
                "Uses",
                "Source",
                "Registered (STARfox)",
                "Registered (Firefox)",
                "Examples",
            ],
            rows,
        )
    )


def _imports(inv):
    rows = [
        [
            f"`{i['module']}`",
            i["category"],
            i["distribution"],
            {True: "yes", False: "no", None: "unknown"}[i["available_in_firefox"]],
            i["files"],
            _short(i["suites"], 4),
            _short(i["locations"], 2),
        ]
        for i in inv["imports"]
        if i["category"] != "stdlib"
    ]
    stdlib = [i["module"] for i in inv["imports"] if i["category"] == "stdlib"]
    return ["## Imports", "", f"Standard library: {_short(stdlib, 40)}.", ""] + _table(
        [
            "Module",
            "Category",
            "Distribution",
            "Available in Firefox",
            "Files",
            "Suites",
            "Examples",
        ],
        rows,
    )


ASSET_TABLES = (
    ("repo_path", "Repo paths, by first folder", None),
    ("url", "URLs, by host", 40),
    ("system_path", "System paths", None),
    ("file_url", "file:// URLs", 10),
    ("file_ref", "File names", 30),
)


def _asset_key(a: dict) -> str:
    if a["kind"] == "repo_path":
        return a["value"].split("/")[0]
    if a["kind"] == "url":
        return url_host(a["value"])
    return a["value"]


def _where(file: str) -> str:
    """Suite folder for a test path, or the file itself for root files."""
    parts = file.split("/")
    return parts[1] if len(parts) > 2 else file


def _facts(inv):
    facts = inv["facts"]
    md = [
        "## Local files, URLs and system paths",
        "",
        "`repo_path` strings are relative to the STARfox root, so they depend on pytest's "
        "working directory (DTE-5558).",
        "",
    ]
    for kind, title, limit in ASSET_TABLES:
        groups = defaultdict(list)
        for a in facts.get("asset", []):
            if a["kind"] == kind:
                groups[_asset_key(a)].append(a)
        rows = [
            [
                f"`{value}`",
                len(items),
                _short(sorted({_where(i["file"]) for i in items}), 5),
                _short([f"{i['file']}:{i['line']}" for i in items], 2),
            ]
            for value, items in sorted(
                groups.items(), key=lambda kv: (-len(kv[1]), kv[0])
            )
        ]
        md += [f"### {title}", ""]
        md += _table(["Value", "Refs", "Where", "Examples"], rows, limit)
    env = defaultdict(list)
    for e in facts.get("env_var", []):
        env[e["value"]].append(e)
    rows = [
        [
            f"`{k}`",
            _short(sorted({e["kind"] for e in v})),
            len(v),
            _short([f"{e['file']}:{e['line']}" for e in v], 3),
        ]
        for k, v in sorted(env.items())
    ]
    md += ["## Environment variables", ""] + _table(
        ["Variable", "Access", "Refs", "Locations"], rows
    )
    wd = facts.get("webdriver", [])
    md += ["## Browser and WebDriver dependencies", ""]
    for kind, title in (
        ("selenium_api", "Selenium APIs"),
        ("browser_arg", "Browser arguments"),
        ("pref", "Pref-like names"),
        ("script", "execute_script calls"),
    ):
        counts = Counter(w["value"] for w in wd if w["kind"] == kind)
        md += [
            f"- **{title}** ({sum(counts.values())} refs): {_short([f'{k} ({n})' for k, n in counts.most_common()], 15)}"
        ]
    cmds = Counter(c["value"] for c in facts.get("command", []))
    md += [
        f"- **External commands**: {_short([f'{k} ({n})' for k, n in cmds.most_common()], 15)}",
        "",
    ]
    return md


def _suites(inv):
    rows = [
        [
            s,
            d["tests"],
            d["tests_with_missing_fixtures"],
            _short(
                [
                    f"{k} ({v})"
                    for k, v in sorted(
                        d["missing_after_migration"].items(), key=lambda kv: -kv[1]
                    )
                ],
                4,
            ),
            d["repo_paths"],
            _short(d["urls"], 3),
            _short(d["env_vars"], 3),
            _short(d["repo_local_imports"], 2),
            _short(d["unregistered_markers_in_firefox"], 4),
        ]
        for s, d in inv["suites"].items()
    ]
    return ["## Suites", "", "Readiness inputs for DTE-5559.", ""] + _table(
        [
            "Suite",
            "Tests",
            "Tests missing fixtures",
            "Missing (tests)",
            "Repo paths",
            "URL hosts",
            "Env vars",
            "Repo-local imports",
            "Markers unregistered in Firefox",
        ],
        rows,
    )


def _unresolved_refs(inv):
    rows = [
        [
            f"`{r['name']}`",
            r["tests"],
            "yes" if r["possibly_generated"] else "no",
            _short(r["requesters"], 2),
        ]
        for r in inv["unresolved_references"]
    ]
    return [
        "## Names nothing provides in STARfox",
        "",
        "Usually a plugin not in the scanned environment, a parametrize the parser missed, "
        "or a real bug.",
        "",
    ] + _table(["Name", "Tests", "Possibly generated", "Requested by"], rows, 50)


def write_all(inv: dict, out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = [
        out_dir / "inventory.json",
        out_dir / "inventory.md",
        out_dir / "fixtures-starfox.dot",
        out_dir / "fixtures-firefox.dot",
    ]
    write_json(inv, paths[0])
    write_markdown(inv, paths[1])
    write_dot(inv, "starfox", paths[2])
    write_dot(inv, "firefox", paths[3])
    return paths
