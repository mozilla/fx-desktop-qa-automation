"""Find conftests, test files and suites in a repo without importing anything."""

import fnmatch
from dataclasses import dataclass, field
from pathlib import Path

EXCLUDED_DIRS = {
    ".git",
    ".hg",
    ".venv",
    "venv",
    ".tox",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    "site-packages",
}


@dataclass
class Layout:
    repo: Path
    tests_dir: Path
    root_conftests: list[Path] = field(default_factory=list)
    suite_conftests: list[Path] = field(default_factory=list)
    outside_conftests: list[Path] = field(default_factory=list)
    test_files: list[Path] = field(default_factory=list)
    helper_files: list[Path] = field(default_factory=list)
    excluded_files: list[Path] = field(default_factory=list)
    repo_entries: frozenset[str] = frozenset()
    repo_packages: frozenset[str] = frozenset()

    def rel(self, path: Path) -> str:
        return path.relative_to(self.repo).as_posix()

    def suite_of(self, path: Path) -> str | None:
        try:
            parts = path.relative_to(self.tests_dir).parts
        except ValueError:
            return None
        return parts[0] if len(parts) > 1 else None

    def level_of_conftest(self, path: Path) -> str:
        if path in self.root_conftests:
            return "root"
        return "suite" if self.suite_of(path) else "tests_root"


def walk_py(root: Path):
    """Yield .py files under root, skipping virtualenvs and caches."""
    for path in sorted(root.rglob("*.py")):
        rel_parts = path.relative_to(root).parts
        if any(p in EXCLUDED_DIRS or p.endswith(".egg-info") for p in rel_parts):
            continue
        yield path


def _is_test_file(path: Path, patterns: tuple[str, ...]) -> bool:
    return any(fnmatch.fnmatch(path.name, p) for p in patterns)


def discover(
    repo: Path,
    tests_dir: str = "tests",
    python_files: tuple[str, ...] = ("test_*.py", "*_test.py"),
    exclude_suites: tuple[str, ...] = (),
) -> Layout:
    repo = repo.resolve()
    tests_path = (repo / tests_dir).resolve()
    if not tests_path.is_dir():
        raise FileNotFoundError(f"tests dir not found: {tests_path}")
    entries = frozenset(p.name for p in repo.iterdir() if not p.name.startswith("."))
    packages = frozenset(
        p.stem if p.is_file() else p.name
        for p in repo.iterdir()
        if (p.is_dir() and (p / "__init__.py").exists())
        or (p.is_file() and p.suffix == ".py" and p.stem != "conftest")
    )
    layout = Layout(repo, tests_path, repo_entries=entries, repo_packages=packages)
    ancestors = {tests_path.parent, *tests_path.parent.parents}
    for path in walk_py(repo):
        inside = tests_path in path.parents
        suite = layout.suite_of(path)
        if inside and suite in exclude_suites:
            layout.excluded_files.append(path)
            continue
        if path.name == "conftest.py":
            if inside:
                layout.suite_conftests.append(path)
            elif path.parent in ancestors:
                layout.root_conftests.append(path)
            else:
                layout.outside_conftests.append(path)
        elif inside and _is_test_file(path, python_files):
            layout.test_files.append(path)
        elif inside:
            layout.helper_files.append(path)
    return layout
