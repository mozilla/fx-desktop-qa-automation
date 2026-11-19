"""Data classes shared by the inventory modules."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Finding:
    """One fact found in source, such as an import, env var or asset path."""

    category: str
    kind: str
    value: str
    file: str
    line: int
    detail: str = ""


@dataclass
class FixtureDef:
    name: str
    func_name: str
    file: str
    line: int
    scope: str
    autouse: bool
    has_params: bool
    is_generator: bool
    args: list[str]
    origin: str
    level: str
    suite: str | None = None
    container: str | None = None
    fingerprint: str = ""
    facts: list[Finding] = field(default_factory=list)
    arg_usage: dict[str, list[str]] = field(default_factory=dict)

    @property
    def id(self) -> str:
        holder = f"{self.container}." if self.container else ""
        return f"{self.file}::{holder}{self.name}"

    def dynamic_requests(self) -> list[str]:
        return [
            f.value
            for f in self.facts
            if f.category == "fixture_request" and f.kind == "getfixturevalue"
        ]


@dataclass
class TestItem:
    __test__ = False  # not a pytest test class

    name: str
    file: str
    line: int
    suite: str | None
    args: list[str]
    usefixtures: list[str]
    container: str | None = None
    params: list[str] = field(default_factory=list)
    markers: list[Finding] = field(default_factory=list)
    facts: list[Finding] = field(default_factory=list)

    @property
    def id(self) -> str:
        holder = f"{self.container}::" if self.container else ""
        return f"{self.file}::{holder}{self.name}"


@dataclass
class Hook:
    name: str
    file: str
    line: int
    origin: str
    facts: list[Finding] = field(default_factory=list)


@dataclass
class ModuleInfo:
    rel: str
    kind: str
    origin: str
    suite: str | None = None
    fixtures: list[FixtureDef] = field(default_factory=list)
    tests: list[TestItem] = field(default_factory=list)
    hooks: list[Hook] = field(default_factory=list)
    imports: list[Finding] = field(default_factory=list)
    facts: list[Finding] = field(default_factory=list)
    options_defined: list[Finding] = field(default_factory=list)
    markers_registered: list[Finding] = field(default_factory=list)
    pytest_plugins: list[Finding] = field(default_factory=list)
    generates_tests: bool = False
    parse_error: str | None = None
