"""Read pytest settings (markers, addopts) from ini and toml files."""

import configparser
import shlex
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from .discovery import EXCLUDED_DIRS

INI_SECTIONS = {"pytest.ini": "pytest", "tox.ini": "pytest", "setup.cfg": "tool:pytest"}


@dataclass
class PytestConfig:
    file: str
    markers: list[str] = field(default_factory=list)
    addopts: list[str] = field(default_factory=list)
    options: dict[str, str] = field(default_factory=dict)

    def option_list(self, key: str) -> tuple[str, ...]:
        value = self.options.get(key)
        return tuple(value.split()) if value else ()


def _as_list(value) -> list[str]:
    if isinstance(value, list):
        return [str(v) for v in value]
    return [line.strip() for line in str(value).splitlines() if line.strip()]


def _from_mapping(file: str, data: dict) -> PytestConfig:
    cfg = PytestConfig(file)
    for key, value in data.items():
        if key == "markers":
            cfg.markers = [
                m.split(":", 1)[0].split("(", 1)[0].strip() for m in _as_list(value)
            ]
        elif key == "addopts":
            cfg.addopts = (
                [str(v) for v in value]
                if isinstance(value, list)
                else shlex.split(str(value))
            )
        else:
            cfg.options[key] = (
                " ".join(_as_list(value)) if isinstance(value, list) else str(value)
            )
    return cfg


def read_config(path: Path, display: str) -> PytestConfig | None:
    """Return the pytest settings in one file, or None if it has none."""
    if path.suffix == ".toml":
        try:
            data = tomllib.loads(path.read_text(encoding="utf-8"))
        except (tomllib.TOMLDecodeError, UnicodeDecodeError):
            return None
        tool = data.get("tool", {}).get("pytest")
        if not isinstance(tool, dict):
            return None
        return _from_mapping(display, tool.get("ini_options", tool))
    section = INI_SECTIONS.get(path.name)
    if not section:
        return None
    parser = configparser.ConfigParser(interpolation=None)
    try:
        parser.read(path, encoding="utf-8")
    except configparser.Error:
        return None
    if not parser.has_section(section):
        return None
    return _from_mapping(display, dict(parser.items(section)))


def discover_configs(repo: Path) -> list[PytestConfig]:
    configs = []
    candidates = list(repo.rglob("*.toml")) + [
        p for name in INI_SECTIONS for p in repo.rglob(name)
    ]
    for path in sorted(set(candidates)):
        if any(p in EXCLUDED_DIRS for p in path.relative_to(repo).parts):
            continue
        cfg = read_config(path, path.relative_to(repo).as_posix())
        if cfg:
            configs.append(cfg)
    return configs
