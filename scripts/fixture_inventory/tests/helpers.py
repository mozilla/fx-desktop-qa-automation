import textwrap
from pathlib import Path


def write_files(root: Path, files: dict[str, str]) -> Path:
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(text).lstrip(), encoding="utf-8")
    return root


def fixture(an, fixture_id: str):
    """The analysed fixture definition with this id, e.g. 'conftest.py::driver'."""
    return next(f for m in an.modules for f in m.fixtures if f.id == fixture_id)
