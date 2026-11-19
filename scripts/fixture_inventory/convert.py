"""
Write Firefox-tree versions of STARfox suite conftests, with a per-suite report.

Run from the STARfox root with the same arguments as the inventory, e.g.

    python -m scripts.fixture_inventory.convert --repo . --out /tmp/conftests \\
        --firefox-conftest ~/firefox/testing/dte-ui-test/tests/conftest.py \\
        --firefox-site ~/firefox/python/sites/dte-ui-test.txt \\
        --firefox-site ~/firefox/python/sites/mach.txt \\
        --exclude-suite meta

The repo is only read. Output: <out>/<path under the tests dir>/conftest.py and
conversion-report.{json,md}. --out must be outside --repo and empty, unless
--overwrite is given.
"""

import ast
import builtins
import json
import sys
import warnings
from pathlib import Path, PurePosixPath

from . import migration_rules
from .cli import build_parser, options_from_args
from .inventory import Inventory

LINE_LENGTH = 88
BUILTINS = frozenset(dir(builtins))
DEFS = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)


def _span(node: ast.AST, lines: list[str]) -> tuple[int, int]:
    """1-based inclusive line span of a top-level def, with decorators and comments."""
    start = min([d.lineno for d in getattr(node, "decorator_list", [])] + [node.lineno])
    while start > 1 and lines[start - 2].lstrip().startswith("#"):
        start -= 1
    return start, node.end_lineno


def _remove_spans(source: str, spans: list[tuple[int, int]]) -> str:
    lines = source.splitlines()
    for start, end in sorted(spans, reverse=True):
        del lines[start - 1 : end]
    return "\n".join(lines) + "\n"


def _used_names(source: str) -> set[str]:
    return {n.id for n in ast.walk(ast.parse(source)) if isinstance(n, ast.Name)}


def _top_level_names(source: str) -> set[str]:
    """Names a module binds at top level: imports, defs, classes and assignments."""
    names = set()
    for node in ast.parse(source).body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names |= {(a.asname or a.name).split(".")[0] for a in node.names}
        elif isinstance(node, DEFS):
            names.add(node.name)
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            names |= {
                n.id for t in targets for n in ast.walk(t) if isinstance(n, ast.Name)
            }
    return names


def _free_names(fn: ast.AST) -> set[str]:
    """Names a function reads that it does not define itself."""
    a = fn.args
    local = {x.arg for x in a.posonlyargs + a.args + a.kwonlyargs}
    local |= {x.arg for x in (a.vararg, a.kwarg) if x}
    local |= {
        n.id
        for n in ast.walk(fn)
        if isinstance(n, ast.Name) and isinstance(n.ctx, (ast.Store, ast.Del))
    }
    loads = {
        n.id
        for n in ast.walk(fn)
        if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)
    }
    return loads - local - BUILTINS


def _import_text(node: ast.ImportFrom | ast.Import) -> str:
    """Render an import the way ruff formats it."""
    one_line = ast.unparse(node)
    if len(one_line) <= LINE_LENGTH or isinstance(node, ast.Import):
        return one_line
    names = ",\n".join(
        f"    {a.name} as {a.asname}" if a.asname else f"    {a.name}"
        for a in node.names
    )
    return f"from {'.' * node.level}{node.module or ''} import (\n{names},\n)"


def _rewrite_imports(
    source: str, removable: set[str], rename=None
) -> tuple[str, list[str]]:
    """
    Rename shim modules and drop imported names listed in `removable`.

    Only names the conversion made unused are removable, so imports that were
    already unused (side effects, fixtures pytest registers by name) stay.
    """
    tree = ast.parse(source)
    lines = source.splitlines()
    edits, changes = [], []
    for node in tree.body:
        if not isinstance(node, (ast.Import, ast.ImportFrom)):
            continue
        new = ast.parse(ast.unparse(node)).body[0]
        if isinstance(new, ast.ImportFrom) and rename and new.module in rename:
            changes.append(f"import from {new.module} now from {rename[new.module]}")
            new.module = rename[new.module]
        kept = [
            a
            for a in new.names
            if a.name == "*" or (a.asname or a.name.split(".")[0]) not in removable
        ]
        dropped = [a.name for a in new.names if a not in kept]
        if dropped:
            changes.append(f"removed unused import {', '.join(dropped)}")
        new.names = kept
        if ast.unparse(new) != ast.unparse(node) or not kept:
            edits.append(
                (node.lineno, node.end_lineno, _import_text(new) if kept else None)
            )
    for start, end, text in sorted(edits, reverse=True):
        lines[start - 1 : end] = text.splitlines() if text else []
    return "\n".join(lines) + "\n", changes


def _tidy_blank_lines(source: str) -> str:
    """
    Two blank lines before each top-level definition, as ruff formats it.

    Only lines between top-level statements change; lines inside a statement
    (such as a multi-line string) are kept as they are.
    """
    lines = source.splitlines()
    body = ast.parse(source).body
    starts = {
        _span(node, lines)[0]
        for i, node in enumerate(body)
        if i and isinstance(node, DEFS)
    }
    inside = {
        number
        for node in body
        for number in range(node.lineno, node.end_lineno + 1)
        if number not in starts
    }
    out: list[str] = []
    for number, line in enumerate(lines, 1):
        if number in starts:
            while out and not out[-1].strip():
                out.pop()
            out += ["", ""]
        elif (
            number not in inside
            and not line.strip()
            and len(out) >= 2
            and not out[-1].strip()
            and not out[-2].strip()
        ):
            continue
        out.append(line)
    while out and not out[0].strip():
        out.pop(0)
    while out and not out[-1].strip():
        out.pop()
    return "\n".join(out) + "\n"


def shim_modules(repo: Path, packages) -> dict[str, str]:
    """Repo modules whose only content is `from auto_fxui.X import *`."""
    shims = {}
    for pkg in sorted(packages):
        folder = repo / pkg
        if not folder.is_dir():
            continue
        for path in sorted(folder.glob("*.py")):
            try:
                body = ast.parse(path.read_text(encoding="utf-8")).body
            except SyntaxError:
                continue
            if (
                len(body) == 1
                and isinstance(body[0], ast.ImportFrom)
                and (body[0].module or "").startswith("auto_fxui")
                and [a.name for a in body[0].names] == ["*"]
            ):
                shims[f"{pkg}.{path.stem}"] = body[0].module
    return shims


def check_out_dir(out: Path, repo: Path, overwrite: bool = False):
    """Raise unless `out` is a safe place to write: outside `repo`, and empty."""
    out, repo = out.resolve(), repo.resolve()
    if out == repo or repo in out.parents:
        raise ValueError(
            f"--out {out} is inside --repo {repo}; refusing to write there"
        )
    if out.exists() and any(out.iterdir()) and not overwrite:
        raise FileExistsError(
            f"--out {out} is not empty; pass --overwrite to replace it"
        )


class Converter:
    def __init__(self, inventory: Inventory, data: dict, rules=migration_rules):
        if not data["meta"]["inputs"]["firefox_conftests"]:
            raise ValueError(
                "no Firefox conftest given: the converter needs it to know what "
                "the Firefox tree already provides"
            )
        self.inv = inventory
        self.data = data
        self.rules = rules
        self.repo = inventory.layout.repo
        self.shims = shim_modules(self.repo, inventory.layout.repo_packages)
        self.unavailable = {
            i["module"] for i in data["imports"] if i["available_in_firefox"] is False
        }
        self.by_file: dict[str, list[dict]] = {}
        self.root_fixtures: dict[str, dict] = {}
        for f in data["fixtures"]:
            if f["level"] == "suite":
                self.by_file.setdefault(f["file"], []).append(f)
            elif f["level"] == "root":
                self.root_fixtures.setdefault(f["name"], f)

    def _drop_reason(self, f: dict) -> str | None:
        if f["name"] in self.rules.DROP:
            return self.rules.DROP[f["name"]]
        eq = f.get("firefox_equivalent") or {}
        if eq.get("status") == "code_identical" and not eq["file"].startswith(
            self.inv.tests_rel + "/"
        ):
            return f"code-identical to {eq['file']}:{eq['line']}"
        return None

    def _still_needed(self, f: dict, kept: list[dict]) -> list[str]:
        """Why a fixture removed by a DROP rule is still needed, if it is."""
        why = []
        if f["tests_using_after_migration"]:
            why.append(f"{f['tests_using_after_migration']} test(s) still use it")
        why += [k["name"] for k in kept if f["name"] in k["args"]]
        return why

    def _move_in(self, name: str, target: str) -> tuple[str | None, str | None]:
        """Return (source to append, None) or (None, reason it cannot move)."""
        f = self.root_fixtures.get(name)
        if f is None:
            return None, f"cannot move {name}: no STARfox root fixture has that name"
        source = (self.repo / f["file"]).read_text(encoding="utf-8")
        lines = source.splitlines()
        node = next(
            (
                n
                for n in ast.parse(source).body
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                and n.lineno == f["line"]
            ),
            None,
        )
        if node is None:
            return None, f"cannot move {name}: not found at {f['file']}:{f['line']}"
        missing = sorted(_free_names(node) - _top_level_names(target) - {"pytest"})
        if missing:
            return None, (
                f"cannot move {name}: it needs {missing} from {f['file']}, which the "
                "suite conftest does not define"
            )
        start, end = _span(node, lines)
        return "\n".join(lines[start - 1 : end]), None

    def convert(self, rel: str) -> dict:
        path_in_tests = PurePosixPath(rel).relative_to(self.inv.tests_rel)
        suite = path_in_tests.parts[0]
        source = (self.repo / rel).read_text(encoding="utf-8")
        lines = source.splitlines()
        fixtures = {(f["name"], f["line"]): f for f in self.by_file.get(rel, [])}
        planned, kept = [], []
        for node in ast.parse(source).body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            f = fixtures.get((node.name, node.lineno)) or next(
                (x for x in fixtures.values() if x["func_name"] == node.name), None
            )
            if f is None:
                continue
            if reason := self._drop_reason(f):
                planned.append((f, node, reason))
            else:
                kept.append(f)
        removed, spans, blockers = [], [], []
        for f, node, reason in planned:
            why = self._still_needed(f, kept) if f["name"] in self.rules.DROP else []
            if why:
                kept.append(f)
                blockers.append(
                    f"{f['name']}: DROP rule not applied, still needed ({'; '.join(why)})"
                )
            else:
                removed.append({"fixture": f["name"], "reason": reason})
                spans.append(_span(node, lines))
        out = _remove_spans(source, spans)
        moved = []
        for name, suites in self.rules.MOVE_TO_SUITE.items():
            if suite in suites and name not in {f["name"] for f in kept}:
                text, problem = self._move_in(name, out)
                if problem:
                    blockers.append(problem)
                    continue
                out = out.rstrip("\n") + "\n\n\n" + text + "\n"
                moved.append(name)
        if moved and "pytest" not in _top_level_names(out):
            out = "import pytest\n\n" + out
        removable = _used_names(source) - _used_names(out)
        out, import_changes = _rewrite_imports(out, removable, rename=self.shims)
        out = _tidy_blank_lines(out)
        more_blockers, notes = self._blockers(rel, kept, out)
        blockers = sorted(set(blockers + more_blockers))
        suite_info = self.data["suites"].get(suite, {})
        return {
            "suite": suite,
            "source": rel,
            "output": str(path_in_tests),
            "status": "blocked" if blockers else "ready",
            # What the suite's tests (not this conftest) still need after migration.
            "tests_still_need": dict(
                sorted(suite_info.get("missing_after_migration", {}).items())
            ),
            "tests_repo_local_imports": suite_info.get("repo_local_imports", []),
            "removed": removed,
            "moved_in": moved,
            "import_changes": import_changes,
            "blockers": blockers,
            "notes": notes,
            "kept": [f["name"] for f in kept],
            "text": out,
        }

    def _blockers(self, rel: str, kept: list[dict], text: str):
        blockers, notes = [], []
        kept_ids = {f["id"] for f in kept}
        for f in kept:
            for reason in f["starfox_specific_reasons"]:
                # Imports from re-export shims were rewritten to auto_fxui above.
                if not any(f" {shim}." in reason for shim in self.shims):
                    blockers.append(f"{f['name']}: {reason}")
            for name in f["blocked_after_migration_by"]:
                blockers.append(
                    f"{f['name']}: requests '{name}', which the Firefox tree does not provide"
                )
            if f["category"] == "potentially_redundant":
                notes.append(f"{f['name']}: {f['reasons'][0]} (cleanup candidate)")
        for fact in self.data["facts"].get("asset", []):
            owned = fact.get("owner") == rel or fact.get("owner") in kept_ids
            if fact["file"] == rel and owned and fact["kind"] == "repo_path":
                blockers.append(
                    f"reads repo file '{fact['value']}' at line {fact['line']} (DTE-5558)"
                )
        for node in ast.walk(ast.parse(text)):
            if isinstance(node, ast.Import):
                modules = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0:
                modules = [node.module or ""]
            else:
                continue
            for module in modules:
                if module.split(".")[0] in self.unavailable:
                    blockers.append(
                        f"imports {module}, which the Firefox tree does not install"
                    )
        return sorted(set(blockers)), sorted(set(notes))

    def run(self) -> list[dict]:
        return [self.convert(rel) for rel in self.data["files"]["suite_conftests"]]


def write_outputs(
    results: list[dict], out: Path, repo: Path, overwrite: bool = False
) -> list[Path]:
    check_out_dir(out, repo, overwrite)
    out.mkdir(parents=True, exist_ok=True)
    paths = []
    for r in results:
        path = out / r["output"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(r["text"], encoding="utf-8")
        paths.append(path)
    report = [{k: v for k, v in r.items() if k != "text"} for r in results]
    (out / "conversion-report.json").write_text(json.dumps(report, indent=2) + "\n")
    md = [
        "# Suite conftest conversion",
        "",
        "Status is for the conftest only. The last two columns are what the suite's",
        "tests still need; a suite is not migration-ready until those are clear too.",
        "",
        "| Suite | Conftest | Removed | Moved in | Conftest blockers "
        "| Tests still need (tests) | Tests' STARfox-only imports |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in report:
        need = ", ".join(f"{k} ({v})" for k, v in r["tests_still_need"].items())
        md.append(
            f"| {r['output']} | {r['status']} "
            f"| {', '.join(x['fixture'] for x in r['removed']) or '-'} "
            f"| {', '.join(r['moved_in']) or '-'} "
            f"| {'; '.join(r['blockers']).replace('|', '/') or '-'} "
            f"| {need or '-'} | {', '.join(r['tests_repo_local_imports']) or '-'} |"
        )
    (out / "conversion-report.md").write_text("\n".join(md) + "\n")
    return paths + [out / "conversion-report.json", out / "conversion-report.md"]


def main(argv=None) -> int:
    parser = build_parser(
        prog="fixture_inventory.convert",
        description="Write Firefox-tree versions of STARfox suite conftests.",
    )
    parser.add_argument(
        "--overwrite", action="store_true", help="Allow writing into a non-empty --out"
    )
    args = parser.parse_args(argv)
    opts = options_from_args(args)
    if opts is None:
        return 2
    if not opts.firefox_conftests:
        print("error: --firefox-conftest is required", file=sys.stderr)
        return 2
    try:
        check_out_dir(args.out, opts.repo, args.overwrite)
    except (ValueError, FileExistsError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    inventory = Inventory(opts)
    # STARfox sources with invalid escapes in strings warn when parsed.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", SyntaxWarning)
        results = Converter(inventory, inventory.build()).run()
    write_outputs(results, args.out.resolve(), opts.repo, args.overwrite)
    ready = sum(r["status"] == "ready" for r in results)
    print(
        f"{len(results)} suite conftests converted: {ready} ready, {len(results) - ready} blocked"
    )
    print(args.out.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
