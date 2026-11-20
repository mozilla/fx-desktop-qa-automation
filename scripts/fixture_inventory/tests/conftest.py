from pathlib import Path

import pytest

from ..analysis import Analysis, Options
from .helpers import write_files


@pytest.fixture()
def driver():
    """No browser: replaces STARfox's autouse driver when run with the repo's config."""
    return None


@pytest.fixture()
def make_repo(tmp_path):
    """Return a function that writes files into a fresh repo dir."""

    def _make(files: dict[str, str], name="repo") -> Path:
        files = {"tests/__init__.py": "", **files}
        return write_files(tmp_path / name, files)

    return _make


@pytest.fixture()
def empty_site(tmp_path) -> Path:
    path = tmp_path / "site-packages"
    path.mkdir()
    return path


@pytest.fixture()
def analyse(tmp_path, empty_site):
    """Return a function that analyses a repo, with an optional Firefox side."""

    def _run(repo: Path, firefox: dict[str, str] | None = None, site_packages=None):
        ff_root = write_files(tmp_path / "firefox", firefox or {})
        opts = Options(
            repo=repo,
            firefox_root=ff_root,
            firefox_conftests=sorted(ff_root.rglob("conftest.py")),
            firefox_sites=sorted((ff_root / "python" / "sites").glob("*.txt")),
            site_packages=[site_packages or empty_site],
        )
        return Analysis(opts).build()

    return _run
