import hashlib
import json

from ..cli import main
from ..config import read_config
from .helpers import write_files

PYPROJECT = """
[tool.pytest.ini_options]
addopts = "-vs --ci -m 'not headed'"
markers = [
  "headed: needs a display",
  "slow: takes long",
]
"""


def test_read_toml_and_ini_configs(tmp_path):
    files = write_files(
        tmp_path,
        {
            "pyproject.toml": PYPROJECT,
            "pytest.ini": "[pytest]\nmarkers =\n    audio: sound\naddopts = -x\n",
            "other.toml": "[tool.ruff]\nline-length = 1\n",
        },
    )
    toml = read_config(files / "pyproject.toml", "pyproject.toml")
    assert toml.markers == ["headed", "slow"]
    assert toml.addopts == ["-vs", "--ci", "-m", "not headed"]
    ini = read_config(files / "pytest.ini", "pytest.ini")
    assert (ini.markers, ini.addopts) == (["audio"], ["-x"])
    assert read_config(files / "other.toml", "other.toml") is None


def test_addopts_flags_and_markers(make_repo, run_inventory):
    repo = make_repo(
        {
            "pyproject.toml": PYPROJECT,
            "conftest.py": 'def pytest_addoption(parser):\n    parser.addoption("--ci")\n',
            "tests/a/test_a.py": "import pytest\n\n@pytest.mark.headed\ndef test_a():\n    pass\n",
        }
    )
    config = run_inventory(repo)["config"]
    flags = {f["flag"]: f for f in config["starfox"][0]["addopts_flags"]}
    assert set(flags) == {"-v", "-s", "--ci", "-m"}
    assert flags["-v"]["provider"] == "pytest" and flags["-v"]["available_in_firefox"]
    assert (
        flags["--ci"]["provider"].startswith("STARfox")
        and not flags["--ci"]["available_in_firefox"]
    )
    (headed,) = config["markers"]
    assert headed["registered_in_starfox"] and not headed["registered_in_firefox"]


def snapshot(root):
    return {
        p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }


def test_cli_writes_reports_and_leaves_the_repo_untouched(
    tmp_path, make_repo, empty_site
):
    repo = make_repo(
        {
            "conftest.py": "import pytest\n\n@pytest.fixture()\ndef base():\n    return 1\n",
            "tests/a/conftest.py": "import pytest\n\n@pytest.fixture()\ndef local(base):\n    return base\n",
            "tests/a/test_a.py": "def test_a(local):\n    pass\n",
        }
    )
    before = snapshot(repo)
    out = tmp_path / "out"
    code = main(
        ["--repo", str(repo), "--out", str(out), "--site-packages", str(empty_site)]
    )
    assert code == 0
    assert snapshot(repo) == before
    names = sorted(p.name for p in out.iterdir())
    assert names == [
        "fixtures-firefox.dot",
        "fixtures-starfox.dot",
        "inventory.json",
        "inventory.md",
    ]
    inv = json.loads((out / "inventory.json").read_text())
    assert inv["meta"]["schema_version"] == 1
    assert [m["name"] for m in inv["missing_after_migration"]] == ["base"]
    md = (out / "inventory.md").read_text()
    for heading in (
        "## Summary",
        "## Missing after migration",
        "## Root conftest fixtures",
        "**Assumptions**",
    ):
        assert heading in md
    assert (
        '"tests/a/conftest.py::local" -> "conftest.py::base"'
        in (out / "fixtures-starfox.dot").read_text()
    )


def test_cli_rejects_missing_firefox_files(tmp_path, make_repo):
    repo = make_repo({"tests/a/test_a.py": "def test_a():\n    pass\n"})
    code = main(
        [
            "--repo",
            str(repo),
            "--out",
            str(tmp_path / "o"),
            "--firefox-conftest",
            str(tmp_path / "nope.py"),
        ]
    )
    assert code == 2
