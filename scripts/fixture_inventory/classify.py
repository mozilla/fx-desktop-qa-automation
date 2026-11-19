"""
Sort fixture definitions into migration categories.

Two definitions with the same name only count as equivalent when their code
(including same-module helpers and constants) is identical. Even then the
report says "code-identical", not "same behaviour".
"""

from dataclasses import dataclass
from pathlib import PurePosixPath

from .models import FixtureDef
from .resolver import World, WorldResult

CATEGORY_LABELS = {
    "available_in_firefox": "Already available in Firefox",
    "missing_required": "Missing and required",
    "potentially_redundant": "Potentially redundant",
    "consumer_removed": "Consumer removed after migration",
    "starfox_specific": "STARfox-specific",
    "unresolved": "Unresolved / needs manual investigation",
    "suite_local": "Moves with its suite or test file",
}
ROOT_LEVELS = ("root",)


@dataclass
class Context:
    sf: World
    ff: World
    sf_res: WorldResult
    ff_res: WorldResult
    defs_by_id: dict[str, FixtureDef]
    shadowed_by: dict[str, list[FixtureDef]]
    repo_packages: frozenset[str]
    firefox_options: set[str]
    starfox_options: set[str]
    imported_helpers: set[str]
    tests_package: str | None = None
    helper_starfox_imports: dict[str, list[str]] | None = None


def option_keys(flag: str) -> set[str]:
    return {flag, flag.lstrip("-").replace("-", "_")}


def compare(a: FixtureDef, b: FixtureDef) -> dict:
    """Describe how two same-name definitions differ in code."""
    if b.origin.startswith(("plugin:", "builtin")):
        return {"status": "provided_by_plugin", "provider": b.origin, "differences": []}
    if a.fingerprint == b.fingerprint:
        return {"status": "code_identical", "differences": []}
    diffs = []
    if a.scope != b.scope:
        diffs.append(f"scope {a.scope} vs {b.scope}")
    if a.autouse != b.autouse:
        diffs.append(f"autouse {a.autouse} vs {b.autouse}")
    if set(a.args) != set(b.args):
        only_a = sorted(set(a.args) - set(b.args))
        only_b = sorted(set(b.args) - set(a.args))
        diffs.append(f"requests only here: {only_a}; only there: {only_b}")
    if a.is_generator != b.is_generator:
        diffs.append("teardown (yield) differs")
    diffs.append("code differs")
    return {"status": "same_name_code_differs", "differences": diffs}


def firefox_provides(name: str, ctx: Context) -> FixtureDef | None:
    """Firefox's own definition of a name: its conftests, plugins or pytest."""
    return ctx.ff.lookup(ctx.ff.root_keys + ctx.ff.plugin_keys, name)[0]


def firefox_provider(d: FixtureDef, ctx: Context) -> FixtureDef | None:
    if d.level in ROOT_LEVELS:
        return firefox_provides(d.name, ctx)
    return ctx.ff.parent_of(d)


def carried_over_dependents(d: FixtureDef, ctx: Context) -> list[str]:
    """Carried-over fixtures that declare this one's name as an argument."""
    return sorted(
        cid
        for ids in ctx.ff_res.carried_over.values()
        for cid in ids
        if cid != d.id and d.name in ctx.defs_by_id[cid].args
    )


def _repo_import_reason(
    module: str, symbol: str, where: str, ctx: Context
) -> str | None:
    top = module.split(".")[0]
    full = f"{module}.{symbol}" if symbol else module
    if module.startswith("."):
        return None
    if ctx.tests_package and top == ctx.tests_package:
        via = (ctx.helper_starfox_imports or {}).get(module)
        return (
            f"uses {full}, which imports STARfox-only {via} ({where})" if via else None
        )
    if top in ctx.repo_packages:
        return f"uses repo-local {full} ({where})"
    return None


def starfox_specific_reasons(d, ctx: Context) -> list[str]:
    """Direct uses of STARfox-only code or CLI options, with locations."""
    reasons = []
    for f in d.facts:
        if f.category == "import":
            symbol = f.detail if f.kind == "used" else ""
            if reason := _repo_import_reason(
                f.value, symbol, f"{f.file}:{f.line}", ctx
            ):
                reasons.append(reason)
        elif f.category == "cli_option" and not (
            option_keys(f.value) & ctx.firefox_options
        ):
            reasons.append(
                f"reads CLI option {f.value} that Firefox does not define ({f.file}:{f.line})"
            )
    return sorted(set(reasons))


def unresolved_reasons(d: FixtureDef, ctx: Context) -> list[str]:
    reasons = []
    if d.scope == "dynamic":
        reasons.append("scope is computed at runtime")
    for f in d.facts:
        if f.category == "dynamic":
            reasons.append(f"non-literal {f.kind} at {f.file}:{f.line}")
    for name, info in ctx.sf_res.missing.items():
        if d.id in info["requesters"]:
            reasons.append(f"requests '{name}', which nothing in STARfox provides")
    if d.level == "helper" and d.id not in ctx.imported_helpers:
        reasons.append("defined in a helper module that no test module imports it from")
    return reasons


def lost_overrides(d: FixtureDef, ctx: Context) -> tuple[list[FixtureDef], list[str]]:
    """Overrides consumed in STARfox but by nothing after migration, and what used them."""
    lost, consumers = [], set()
    for o in ctx.shadowed_by.get(d.id, []):
        if ctx.sf_res.used_by_tests.get(o.id) and not ctx.ff_res.used_by_tests.get(
            o.id
        ):
            lost.append(o)
            consumers |= ctx.sf_res.consumers.get(o.id, set())
    return lost, sorted(consumers)


def _consumer_usage(name: str, consumer_ids: list[str], ctx: Context) -> str:
    parts = []
    for cid in consumer_ids:
        c = ctx.defs_by_id.get(cid)
        if c and c.arg_usage.get(name):
            parts.append(f"{c.name}: {', '.join(c.arg_usage[name])}")
    return "; ".join(parts)


def classify(d: FixtureDef, ctx: Context) -> dict:
    used_sf = ctx.sf_res.used_by_tests.get(d.id, set())
    used_ff = ctx.ff_res.used_by_tests.get(d.id, set())
    provider = firefox_provider(d, ctx)
    equivalence = compare(d, provider) if provider else None
    sf_reasons = starfox_specific_reasons(d, ctx)
    notes: list[str] = []
    blocked_by = sorted(
        name for name, info in ctx.ff_res.missing.items() if d.id in info["requesters"]
    )
    if blocked_by and d.level not in ROOT_LEVELS:
        notes.append(f"after migration it requests missing fixtures: {blocked_by}")

    if reasons := unresolved_reasons(d, ctx):
        category = "unresolved"
    elif d.level in ROOT_LEVELS:
        category, reasons = _classify_root(d, ctx, provider, used_sf, sf_reasons, notes)
    else:
        category, reasons = _classify_local(
            d, ctx, provider, used_sf, used_ff, sf_reasons
        )
    if provider and equivalence["status"] == "same_name_code_differs":
        notes.append(
            f"Firefox has a same-name fixture at {provider.file}:{provider.line} "
            "whose code differs; check behaviour before relying on it"
        )
    return {
        "category": category,
        "label": CATEGORY_LABELS[category],
        "reasons": reasons,
        "notes": notes,
        "starfox_specific_reasons": sf_reasons,
        "firefox_equivalent": (
            {
                "id": provider.id,
                "file": provider.file,
                "line": provider.line,
                **equivalence,
            }
            if provider
            else None
        ),
        "blocked_after_migration_by": blocked_by,
    }


def _fixture_consumers(d: FixtureDef, ctx: Context) -> list[str]:
    return sorted(
        c for c in ctx.sf_res.consumers.get(d.id, set()) if c in ctx.defs_by_id
    )


def _removed_reason(consumers: list[str], ctx: Context) -> str:
    """Explain why nothing consumes a fixture after migration."""
    replaced = [c for c in consumers if firefox_provides(ctx.defs_by_id[c].name, ctx)]
    if consumers and len(replaced) == len(consumers):
        return (
            f"only consumed by {consumers}; Firefox replaces them with its own "
            "fixtures, which do not request it"
        )
    return f"only consumed by {consumers}, none of which is used after migration"


def _classify_root(d, ctx, provider, used_sf, sf_reasons, notes):
    if provider:
        return "available_in_firefox", [
            f"Firefox provides '{d.name}' at {provider.file}:{provider.line}"
        ]
    tests = ctx.ff_res.missing.get(d.name, {}).get("tests", set())
    dependents = carried_over_dependents(d, ctx)
    if tests or dependents:
        reasons = []
        if tests:
            reasons.append(f"needed by {len(tests)} test(s) after migration")
        if dependents:
            reasons.append(
                f"declared as an argument by carried-over fixture(s) {dependents}"
            )
        category = "starfox_specific" if sf_reasons else "missing_required"
        return category, reasons
    lost, consumers = lost_overrides(d, ctx)
    if not used_sf and not lost:
        return "potentially_redundant", ["not used by any analysed test"]
    if lost:
        how = _consumer_usage(d.name, consumers, ctx)
        files = sorted({o.file for o in lost})
        return "unresolved", [
            f"{len(files)} file(s) override it to configure {consumers}"
            + (f" (used as: {how})" if how else "")
            + "; after migration nothing requests it, so decide whether Firefox needs this hook"
        ]
    if d.autouse:
        return "unresolved", [
            f"autouse: runs for {len(used_sf)} test(s) in STARfox for its side effects; "
            "Firefox has no fixture of this name, so decide whether that effect is needed"
        ]
    if d.name in ctx.ff_res.optional_missing:
        requesters = sorted(ctx.ff_res.optional_missing[d.name])
        return "unresolved", [
            f"only requested through getfixturevalue by {requesters}; check whether those "
            "code paths run after migration"
        ]
    return "consumer_removed", [_removed_reason(_fixture_consumers(d, ctx), ctx)]


def _classify_local(d, ctx, provider, used_sf, used_ff, sf_reasons):
    parent_sf = ctx.sf.parent_of(d)
    if provider and provider.fingerprint == d.fingerprint:
        return "potentially_redundant", [
            f"code-identical to {provider.file}:{provider.line}, which it would shadow in Firefox"
        ]
    if parent_sf and parent_sf.fingerprint == d.fingerprint:
        return "potentially_redundant", [
            f"code-identical to {parent_sf.file}:{parent_sf.line}, which it shadows"
        ]
    if not used_sf and not used_ff:
        return "potentially_redundant", ["not used by any analysed test"]
    if sf_reasons:
        return "starfox_specific", ["depends on STARfox-only code or options"]
    if used_sf and not used_ff:
        return "consumer_removed", [_removed_reason(_fixture_consumers(d, ctx), ctx)]
    return "suite_local", ["self-contained; moves with its suite or test file"]


def locality_of(d: FixtureDef, test_ids: set[str]) -> dict:
    """Count tests that get the fixture from their own dir/file vs a parent conftest."""
    home = PurePosixPath(d.file)
    local = inherited = 0
    for tid in test_ids:
        tfile = PurePosixPath(tid.split("::")[0])
        same = (
            tfile == home
            if d.level in ("module", "class")
            else tfile.parent == home.parent
        )
        local += same
        inherited += not same
    return {"same_location": local, "inherited_from_parent": inherited}
