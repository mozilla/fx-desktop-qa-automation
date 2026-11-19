"""
Installed packages, pytest plugins and Firefox mach site files.

Package metadata and plugin source are read from disk; nothing is imported.
"""

import re
import sys
from dataclasses import dataclass, field
from importlib import metadata
from pathlib import Path

from .models import Finding

SITE_PREFIXES = ("pypi", "pypi-optional", "pth", "vendored", "packages.txt")


def normalize(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def _requirement_name(req: str) -> str | None:
    if "extra ==" in req.replace("'", '"').replace('"', ""):
        return None
    m = re.match(r"\s*([A-Za-z0-9][A-Za-z0-9._-]*)", req)
    return normalize(m.group(1)) if m else None


@dataclass
class Distribution:
    name: str
    version: str
    top_level: set[str] = field(default_factory=set)
    requires: list[str] = field(default_factory=list)
    plugin_files: list[tuple[str, Path]] = field(default_factory=list)
    files: list[Path] = field(default_factory=list)


def _package_dirs(path: Path) -> set[str]:
    if not path.is_dir():
        return set()
    return {
        p.stem if p.is_file() else p.name
        for p in path.iterdir()
        if (p.is_dir() and (p / "__init__.py").exists())
        or (p.is_file() and p.suffix == ".py" and p.stem not in ("setup", "conftest"))
    }


def _load(dist: metadata.Distribution) -> Distribution | None:
    name = dist.metadata["Name"]
    if not name:
        return None
    files = [Path(dist.locate_file(f)) for f in (dist.files or [])]
    declared = set((dist.read_text("top_level.txt") or "").split())
    derived, editable = set(), set()
    for f, local in zip(dist.files or [], files):
        parts = f.parts
        if (
            not parts
            or parts[0] in ("..", "bin")
            or parts[0].endswith((".dist-info", ".egg-info"))
        ):
            continue
        if f.suffix == ".pth" and local.exists():
            for line in local.read_text(encoding="utf-8", errors="ignore").splitlines():
                if line and not line.startswith(("#", "import ")):
                    editable |= _package_dirs(Path(line.strip()))
        elif f.suffix == ".py":
            derived.add(parts[0] if len(parts) > 1 else f.stem)
    top = (declared or derived) | editable
    plugin_files = []
    for ep in dist.entry_points:
        if ep.group != "pytest11":
            continue
        module = ep.value.split(":")[0].strip()
        stem = module.replace(".", "/")
        for f, local in zip(dist.files or [], files):
            if f.as_posix() in (f"{stem}.py", f"{stem}/__init__.py"):
                plugin_files.append((module, local))
    requires = [r for r in (_requirement_name(x) for x in dist.requires or []) if r]
    return Distribution(
        normalize(name),
        dist.version,
        top - {"__pycache__"},
        requires,
        plugin_files,
        files,
    )


class Environment:
    """Packages visible in the given site-packages dirs (default: this Python)."""

    def __init__(self, paths: list[Path] | None = None):
        self.paths = paths
        found = (
            metadata.distributions(path=[str(p) for p in paths])
            if paths
            else metadata.distributions()
        )
        self.dists: dict[str, Distribution] = {}
        for d in found:
            loaded = _load(d)
            if loaded and loaded.name not in self.dists:
                self.dists[loaded.name] = loaded
        self.module_to_dist = {
            mod: d.name for d in self.dists.values() for mod in sorted(d.top_level)
        }

    def closure(self, names: set[str]) -> tuple[set[str], set[str]]:
        """Return (dists reachable through requirements, names not installed here)."""
        seen, unknown, stack = set(), set(), [normalize(n) for n in names]
        while stack:
            n = stack.pop()
            if n in seen or n in unknown:
                continue
            if n not in self.dists:
                unknown.add(n)
                continue
            seen.add(n)
            stack.extend(self.dists[n].requires)
        return seen, unknown

    def pytest_builtin_files(self) -> tuple[list[Path], str]:
        """Return pytest's own modules, used to find built-in fixtures and markers."""
        dist = self.dists.get("pytest")
        source = "scanned environment"
        if dist is None:
            try:
                dist = _load(metadata.distribution("pytest"))
                source = "the Python running this tool"
            except metadata.PackageNotFoundError:
                return [], "not found"
        files = [
            f
            for f in dist.files
            if f.suffix == ".py" and "_pytest" in f.parts and f.exists()
        ]
        return files, f"pytest {dist.version} from {source}"


@dataclass
class FirefoxSite:
    files: list[str] = field(default_factory=list)
    pypi: list[Finding] = field(default_factory=list)
    local: list[Finding] = field(default_factory=list)
    modules: set[str] = field(default_factory=set)
    notes: list[str] = field(default_factory=list)


def _site_root(site_file: Path, fallback: Path | None) -> Path | None:
    """Return the tree root for python/sites/<name>.txt, else the fallback."""
    if site_file.parent.name == "sites" and site_file.parent.parent.name == "python":
        return site_file.parents[2]
    return fallback


def parse_firefox_sites(files: list[Path], firefox_root: Path | None) -> FirefoxSite:
    site = FirefoxSite()
    queue = list(files)
    seen = set()
    while queue:
        path = queue.pop(0).resolve()
        if path in seen:
            continue
        seen.add(path)
        site.files.append(str(path))
        root = _site_root(path, firefox_root)
        for n, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            line = raw.strip()
            if not line or line.startswith("#") or ":" not in line:
                continue
            prefix, _, rest = line.partition(":")
            if prefix in ("pypi", "pypi-optional"):
                spec = rest.split(":")[0]
                name = _requirement_name(spec)
                if name:
                    site.pypi.append(Finding("site", prefix, name, str(path), n, spec))
            elif prefix in ("pth", "vendored"):
                names = _package_dirs(root / rest) if root else set()
                if root and (root / rest / "__init__.py").exists():
                    names.add(Path(rest).name)
                site.modules |= names
                site.local.append(
                    Finding("site", prefix, rest, str(path), n, ",".join(sorted(names)))
                )
                if not root:
                    site.notes.append(f"{path}:{n}: no tree root to resolve {rest}")
            elif prefix == "packages.txt" and root:
                queue.append(root / rest)
    return site


def stdlib_modules() -> frozenset[str]:
    return frozenset(sys.stdlib_module_names)
