"""
Resolve each test's fixture closure the way pytest does, without running it.

Names resolve from the test's location, nearest definition first:
test class, test module, conftests from the test's dir upwards, plugins,
then pytest built-ins. A fixture requesting its own name gets the next
definition up the chain.

A world can also have carry-over layers, searched last: definitions that do
not exist there yet but would have to be brought along (for the Firefox world,
the STARfox root conftest and plugins Firefox does not install). A name found
only there is recorded as missing, and resolution continues through that
definition so its own dependencies are found too.
"""

from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import PurePosixPath

from .models import FixtureDef, TestItem

# pytest supplies `request` itself rather than through a @fixture definition.
PSEUDO_FIXTURES = frozenset({"request"})

Key = tuple


@dataclass
class WorldResult:
    name: str
    used_by_tests: dict[str, set[str]] = field(default_factory=lambda: defaultdict(set))
    consumers: dict[str, set[str]] = field(default_factory=lambda: defaultdict(set))
    edges: dict[tuple[str, str], int] = field(default_factory=lambda: defaultdict(int))
    missing: dict[str, dict[str, set[str]]] = field(
        default_factory=lambda: defaultdict(
            lambda: {"tests": set(), "requesters": set()}
        )
    )
    optional_missing: dict[str, set[str]] = field(
        default_factory=lambda: defaultdict(set)
    )
    carried_over: dict[str, set[str]] = field(default_factory=lambda: defaultdict(set))
    per_test: dict[str, dict] = field(default_factory=dict)


class World:
    """One view of where fixtures come from, e.g. STARfox today or after migration."""

    def __init__(self, name: str, tests_dir: str, root_keys: list[Key]):
        self.name = name
        self.tests_dir = PurePosixPath(tests_dir)
        self.root_keys = root_keys
        self.plugin_keys: list[Key] = []
        self.carry_over_keys: list[Key] = []
        self.layers: dict[Key, dict[str, FixtureDef]] = defaultdict(dict)
        self.same_layer_duplicates: list[tuple[FixtureDef, FixtureDef]] = []

    def add(self, key: Key, fixture: FixtureDef):
        layer = self.layers[key]
        if fixture.name in layer and layer[fixture.name] is not fixture:
            self.same_layer_duplicates.append((layer[fixture.name], fixture))
        layer[fixture.name] = fixture
        if key[0] in ("plugin", "builtin") and key not in self.plugin_keys:
            self.plugin_keys.append(key)

    def add_carry_over(self, key: Key, fixture: FixtureDef):
        """Add a definition that this world lacks but could bring along."""
        key = ("carry_over", *key)
        self.layers[key][fixture.name] = fixture
        if key not in self.carry_over_keys:
            self.carry_over_keys.append(key)

    def chain_for(
        self, file: str, container: str | None = None, carry_over: bool = True
    ) -> list[Key]:
        path = PurePosixPath(file)
        chain: list[Key] = []
        if container:
            chain.append(("class", file, container))
        chain.append(("module", file))
        for d in [path.parent, *path.parent.parents]:
            if d == self.tests_dir or self.tests_dir in d.parents:
                chain.append(("dir", d.as_posix()))
        chain.extend(self.root_keys)
        builtin = [k for k in self.plugin_keys if k[0] == "builtin"]
        chain.extend([k for k in self.plugin_keys if k[0] == "plugin"] + builtin)
        if carry_over:
            chain.extend(self.carry_over_keys)
        return chain

    def lookup(self, chain: list[Key], name: str, start: int = 0):
        for i in range(start, len(chain)):
            layer = self.layers.get(chain[i])
            if layer and name in layer:
                return layer[name], i
        return None, -1

    def index_of(self, chain: list[Key], fixture: FixtureDef) -> int:
        for i, key in enumerate(chain):
            if self.layers.get(key, {}).get(fixture.name) is fixture:
                return i
        return -1

    def parent_of(self, fixture: FixtureDef) -> FixtureDef | None:
        """Return the definition this world provides that this one shadows."""
        chain = self.chain_for(fixture.file, fixture.container, carry_over=False)
        idx = self.index_of(chain, fixture)
        if idx < 0:
            return None
        return self.lookup(chain, fixture.name, idx + 1)[0]

    def autouse_names(self, chain: list[Key]) -> list[str]:
        names = []
        for key in chain:
            if key[0] == "carry_over":
                continue
            for f in self.layers.get(key, {}).values():
                if f.autouse and f.name not in names:
                    names.append(f.name)
        return names

    def resolve(self, tests: list[TestItem]) -> WorldResult:
        result = WorldResult(self.name)
        for test in tests:
            chain = self.chain_for(test.file, test.container)
            used, missing, carried = self._closure(test, chain, result)
            result.per_test[test.id] = {
                "fixtures": sorted(used - carried),
                "missing": sorted(missing),
                "carried_over": sorted(carried),
            }
        return result

    def _closure(self, test: TestItem, chain: list[Key], result: WorldResult):
        queue = [
            (n, test.id, 0, False)
            for n in self.autouse_names(chain) + test.usefixtures + test.args
        ]
        used: set[str] = set()
        missing: set[str] = set()
        carried: set[str] = set()
        while queue:
            name, requester, start, optional = queue.pop(0)
            # Directly parametrized names are visible to the test's fixtures too.
            if name in PSEUDO_FIXTURES or name in test.params:
                continue
            fixture, idx = self.lookup(chain, name, start)
            is_carried = fixture is not None and chain[idx][0] == "carry_over"
            if fixture is None or is_carried:
                if optional:
                    result.optional_missing[name].add(requester)
                    continue
                missing.add(name)
                result.missing[name]["tests"].add(test.id)
                result.missing[name]["requesters"].add(requester)
                if fixture is None:
                    continue
                carried.add(fixture.id)
                result.carried_over[name].add(fixture.id)
            result.edges[(requester, fixture.id)] += 1
            result.consumers[fixture.id].add(requester)
            result.used_by_tests[fixture.id].add(test.id)
            if fixture.id in used:
                continue
            used.add(fixture.id)
            # getfixturevalue calls are often guarded, so a missing one is optional.
            requests = [(a, False) for a in fixture.args]
            requests += [(a, True) for a in fixture.dynamic_requests()]
            for arg, opt in requests:
                start = idx + 1 if arg == fixture.name else 0
                queue.append((arg, fixture.id, start, opt))
        return used, missing, carried
