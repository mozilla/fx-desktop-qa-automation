"""Static extraction of fixtures, tests, hooks and facts from one Python module."""

import ast
import fnmatch
import hashlib
import re
from urllib.parse import urlparse

from .models import Finding, FixtureDef, Hook, ModuleInfo, TestItem

URL_RE = re.compile(r"^(https?|wss?|ftp|file)://", re.IGNORECASE)
FILE_EXT_RE = re.compile(
    r"^[\w\-. {}/\\]*[\w\-{}]\.(html?|xhtml|pdf|zip|png|jpe?g|gif|svg|webp|ico|json"
    r"|txt|csv|xml|mp4|webm|ogg|ogv|mp3|wav|xpi|crx|ics|vcf|dmg|exe|ya?ml|toml)$",
    re.IGNORECASE,
)
PREF_RE = re.compile(r"^[a-z][\w-]*(\.[\w-]+)+$")
WIN_DRIVE_RE = re.compile(r"^[A-Za-z]:[\\/]")
SYSTEM_ROOTS = {
    "Applications",
    "Library",
    "System",
    "Users",
    "Volumes",
    "bin",
    "dev",
    "etc",
    "home",
    "opt",
    "private",
    "proc",
    "sbin",
    "tmp",
    "usr",
    "var",
}
PATH_FUNCS = {
    "pathlib.Path",
    "pathlib.PurePath",
    "pathlib.PurePosixPath",
    "pathlib.PureWindowsPath",
    "os.path.join",
}
COMMAND_FUNCS = {
    "subprocess.run",
    "subprocess.call",
    "subprocess.check_call",
    "subprocess.check_output",
    "subprocess.Popen",
    "os.system",
    "os.popen",
}
ENV_READ = {"os.environ.get", "os.getenv"}
ENV_WRITE = {"os.environ.pop", "os.environ.setdefault", "os.putenv", "os.unsetenv"}
FIXTURE_DECORATORS = {"fixture", "yield_fixture"}


def url_host(url: str) -> str:
    """Return the URL's host, or the URL itself if it can't be parsed."""
    try:
        return urlparse(url).hostname or url
    except ValueError:
        return url


def dotted(node: ast.AST) -> str | None:
    """Return 'a.b.c' for a Name/Attribute chain, else None."""
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
        return ".".join(reversed(parts))
    return None


def literal_str(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def literal_strs(node: ast.AST) -> list[str] | None:
    """Return the strings of a str/list/tuple literal; None if not literal."""
    if (s := literal_str(node)) is not None:
        return [s]
    if isinstance(node, (ast.List, ast.Tuple)):
        values = [literal_str(e) for e in node.elts]
        return None if None in values else values
    return None


def _strip_docstring(body: list[ast.stmt]) -> list[ast.stmt]:
    if body and isinstance(body[0], ast.Expr) and literal_str(body[0].value):
        return body[1:]
    return body


def local_names(node: ast.AST) -> set[str]:
    """Parameters and assigned names of a function, which shadow module names."""
    if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
        return set()
    a = node.args
    names = {x.arg for x in a.posonlyargs + a.args + a.kwonlyargs}
    names |= {x.arg for x in (a.vararg, a.kwarg) if x}
    names |= {
        n.id
        for n in ast.walk(node)
        if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store)
    }
    return names


def _first_use_only(findings: list[Finding]) -> list[Finding]:
    """Keep the first use of each imported name; keep every other finding."""
    seen, out = set(), []
    for f in findings:
        if f.kind in ("used", "selenium_api"):
            key = (f.category, f.kind, f.value, f.detail)
            if key in seen:
                continue
            seen.add(key)
        out.append(f)
    return out


def _matches(name: str, patterns: tuple[str, ...]) -> bool:
    return any(
        fnmatch.fnmatch(name, p) if "*" in p else name.startswith(p) for p in patterns
    )


class ModuleParser:
    def __init__(
        self,
        source: str,
        rel: str,
        *,
        kind: str,
        origin: str,
        level: str,
        suite: str | None = None,
        repo_entries: frozenset[str] = frozenset(),
        python_functions: tuple[str, ...] = ("test",),
        python_classes: tuple[str, ...] = ("Test",),
    ):
        self.rel = rel
        self.kind = kind
        self.origin = origin
        self.level = level
        self.suite = suite
        self.repo_entries = repo_entries
        self.python_functions = python_functions
        self.python_classes = python_classes
        self.tree = ast.parse(source)
        self.imports: dict[str, tuple[str, str]] = {}
        self.functions: dict[str, ast.FunctionDef] = {}
        self.constants: dict[str, ast.AST] = {}
        self.docstrings: set[int] = set()
        self._index_module()
        self.fixture_funcs = {
            name
            for name, fn in self.functions.items()
            if any(self._is_fixture_decorator(d) for d in fn.decorator_list)
        }

    # Module indexing

    def _index_module(self):
        for node in ast.walk(self.tree):
            if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef)):
                body = node.body
            elif isinstance(node, ast.ClassDef):
                body = node.body
            else:
                continue
            if body and isinstance(body[0], ast.Expr) and literal_str(body[0].value):
                self.docstrings.add(id(body[0].value))
        for node in self.tree.body:
            if isinstance(node, ast.Import):
                for a in node.names:
                    local = a.asname or a.name.split(".")[0]
                    self.imports[local] = (a.name if a.asname else local, "")
            elif isinstance(node, ast.ImportFrom):
                mod = "." * node.level + (node.module or "")
                for a in node.names:
                    self.imports[a.asname or a.name] = (mod, a.name)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self.functions[node.name] = node
            elif isinstance(node, (ast.Assign, ast.AnnAssign)):
                targets = (
                    node.targets if isinstance(node, ast.Assign) else [node.target]
                )
                for t in targets:
                    if isinstance(t, ast.Name) and node.value is not None:
                        self.constants[t.id] = node

    def resolve(self, node: ast.AST) -> str | None:
        """Qualify a Name/Attribute chain using this module's imports."""
        name = dotted(node)
        if name is None:
            return None
        head, _, rest = name.partition(".")
        if head in self.imports:
            mod, sym = self.imports[head]
            base = f"{mod}.{sym}" if sym else mod
            return f"{base}.{rest}" if rest else base
        return name

    # Fact collection

    def _finding(self, category, kind, value, node, detail=""):
        return Finding(category, kind, str(value), self.rel, node.lineno, detail)

    def classify_string(self, s: str, node: ast.AST, detail="") -> Finding | None:
        if not s or "\n" in s or len(s) > 400:
            return None
        if URL_RE.match(s):
            kind = "file_url" if s.lower().startswith("file:") else "url"
            return self._finding("asset", kind, s, node, detail)
        parts = [p for p in re.split(r"[\\/]", s) if p]
        if WIN_DRIVE_RE.match(s) or (
            s.startswith("/")
            and not s.startswith("//")
            and parts
            and parts[0] in SYSTEM_ROOTS
        ):
            return self._finding("asset", "system_path", s, node, detail)
        if (
            not s.startswith(("/", "."))
            and len(parts) > 1
            and parts[0] in self.repo_entries
        ):
            return self._finding("asset", "repo_path", s, node, detail)
        if FILE_EXT_RE.match(s):
            return self._finding("asset", "file_ref", s, node, detail)
        return None

    def collect_facts(self, root: ast.AST, visited: set[str] | None = None, via=""):
        visited = set() if visited is None else visited
        shadowed = local_names(root)
        out: list[Finding] = []
        skip: set[int] = set()
        for node in ast.walk(root):
            if id(node) in skip or id(node) in self.docstrings:
                continue
            if isinstance(node, ast.Import):
                for a in node.names:
                    out.append(self._finding("import", "import", a.name, node, via))
            elif isinstance(node, ast.ImportFrom):
                mod = "." * node.level + (node.module or "")
                names = ",".join(a.name for a in node.names)
                out.append(self._finding("import", "import", mod, node, names))
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                if node.id not in shadowed:
                    out.extend(self._name_facts(node, visited, via))
            elif isinstance(node, ast.Call):
                out.extend(self._call_facts(node, skip, via))
            elif isinstance(node, ast.Subscript):
                key = literal_str(node.slice)
                if key and self.resolve(node.value) == "os.environ":
                    kind = "read" if isinstance(node.ctx, ast.Load) else "write"
                    out.append(self._finding("env_var", kind, key, node, via))
                elif (
                    key
                    and isinstance(node.value, ast.Attribute)
                    and node.value.attr == "funcargs"
                ):
                    out.append(self._finding("fixture_request", "funcargs", key, node))
            elif isinstance(node, ast.Compare):
                key = literal_str(node.left)
                if (
                    key
                    and isinstance(node.ops[0], (ast.In, ast.NotIn))
                    and self.resolve(node.comparators[0]) == "os.environ"
                ):
                    out.append(self._finding("env_var", "read", key, node, via))
            elif isinstance(node, ast.JoinedStr):
                text = "".join(
                    v.value if isinstance(v, ast.Constant) else "{}"
                    for v in node.values
                )
                skip.update(id(v) for v in ast.walk(node) if v is not node)
                if f := self.classify_string(text, node, via):
                    out.append(f)
            elif isinstance(node, ast.Tuple) and len(node.elts) == 2:
                key = literal_str(node.elts[0])
                if (
                    key
                    and PREF_RE.match(key)
                    and isinstance(
                        node.elts[1], (ast.Constant, ast.Attribute, ast.Name)
                    )
                ):
                    out.append(self._finding("webdriver", "pref", key, node, via))
            elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                if f := self.classify_string(node.value, node, via):
                    out.append(f)
        return _first_use_only(out)

    def _name_facts(self, node: ast.Name, visited: set[str], via: str):
        out = []
        if node.id in self.imports:
            mod, sym = self.imports[node.id]
            out.append(self._finding("import", "used", mod, node, sym))
            qualified = f"{mod}.{sym}" if sym else mod
            if qualified.startswith("selenium"):
                out.append(self._finding("webdriver", "selenium_api", qualified, node))
        elif (
            node.id in self.functions
            and node.id not in visited
            and node.id not in self.fixture_funcs
        ):
            visited.add(node.id)
            out.extend(
                self.collect_facts(self.functions[node.id], visited, f"via {node.id}()")
            )
        elif node.id in self.constants and node.id not in visited:
            visited.add(node.id)
            out.extend(
                self.collect_facts(self.constants[node.id], visited, f"via {node.id}")
            )
        return out

    def _call_facts(self, node: ast.Call, skip: set[int], via: str):
        out = []
        q = self.resolve(node.func) or ""
        attr = node.func.attr if isinstance(node.func, ast.Attribute) else ""
        first = node.args[0] if node.args else None
        first_str = literal_str(first) if first is not None else None
        holder = node.func.value if isinstance(node.func, ast.Attribute) else None
        if (
            attr == "get"
            and isinstance(holder, ast.Attribute)
            and holder.attr == "funcargs"
        ):
            if first_str:
                out.append(
                    self._finding("fixture_request", "funcargs", first_str, node)
                )
        elif attr == "getfixturevalue":
            if first_str:
                out.append(
                    self._finding("fixture_request", "getfixturevalue", first_str, node)
                )
            else:
                out.append(self._finding("dynamic", "getfixturevalue", "<expr>", node))
        elif attr in ("getoption", "getvalue") and first_str:
            out.append(self._finding("cli_option", "read", first_str, node, via))
        elif q in ENV_READ | ENV_WRITE and first_str:
            kind = "read" if q in ENV_READ else "write"
            out.append(self._finding("env_var", kind, first_str, node, via))
        elif attr in ("setenv", "delenv") and first_str:
            out.append(self._finding("env_var", "write", first_str, node, via))
        elif attr == "set_preference" and first_str:
            out.append(self._finding("webdriver", "pref", first_str, node, via))
        elif attr == "add_argument" and first_str:
            out.append(self._finding("webdriver", "browser_arg", first_str, node, via))
        elif attr in ("execute_script", "execute_async_script"):
            out.append(self._finding("webdriver", "script", attr, node, via))
        elif q in COMMAND_FUNCS and first is not None:
            cmd = literal_strs(first)
            if cmd is None and isinstance(first, (ast.List, ast.Tuple)) and first.elts:
                cmd = [literal_str(first.elts[0]) or "<expr>"]
            value = (
                (cmd[0].split()[0] if cmd and cmd[0] else "<expr>") if cmd else "<expr>"
            )
            out.append(self._finding("command", q, value, node, via))
        elif q in PATH_FUNCS and first_str is not None:
            literal_parts = []
            for a in node.args:
                s = literal_str(a)
                literal_parts.append(s if s is not None else "{}")
                skip.update(id(n) for n in ast.walk(a))
            head = re.split(r"[\\/]", first_str)[0]
            if head in self.repo_entries:
                path = "/".join(literal_parts)
                out.append(self._finding("asset", "repo_path", path, node, via))
            elif f := self.classify_string("/".join(literal_parts), node, via):
                out.append(f)
        return out

    # Structure extraction

    def _is_fixture_decorator(self, dec: ast.AST) -> bool:
        target = dec.func if isinstance(dec, ast.Call) else dec
        name = dotted(target)
        if not name or name.split(".")[-1] not in FIXTURE_DECORATORS:
            return False
        if "." not in name:
            mod = self.imports.get(name, ("", ""))[0]
            return "pytest" in mod or name in self.functions or not self.imports
        q = self.resolve(target) or name
        return "pytest" in q

    def _fixture_def(self, fn, container=None, level=None) -> FixtureDef | None:
        dec = next(
            (d for d in fn.decorator_list if self._is_fixture_decorator(d)), None
        )
        if dec is None:
            return None
        name, scope, autouse, has_params = fn.name, "function", False, False
        if isinstance(dec, ast.Call):
            for kw in dec.keywords:
                if kw.arg == "name" and (s := literal_str(kw.value)):
                    name = s
                elif kw.arg == "scope":
                    scope = literal_str(kw.value) or "dynamic"
                elif kw.arg == "autouse":
                    autouse = (
                        bool(kw.value.value)
                        if isinstance(kw.value, ast.Constant)
                        else True
                    )
                elif kw.arg == "params":
                    has_params = True
            if dec.args and literal_str(dec.args[0]):
                scope = literal_str(dec.args[0])
        is_static = any(dotted(d) == "staticmethod" for d in fn.decorator_list)
        fixture = FixtureDef(
            name=name,
            func_name=fn.name,
            file=self.rel,
            line=fn.lineno,
            scope=scope,
            autouse=autouse,
            has_params=has_params,
            is_generator=any(
                isinstance(n, (ast.Yield, ast.YieldFrom)) for n in ast.walk(fn)
            ),
            args=self._requested_args(fn, method=bool(container) and not is_static),
            origin=self.origin,
            level=level or self.level,
            suite=self.suite,
            container=container,
        )
        fixture.facts = self.collect_facts(fn)
        fixture.fingerprint = self.fingerprint(fn)
        fixture.arg_usage = self.arg_usage(fn, fixture.args)
        return fixture

    @staticmethod
    def arg_usage(fn, args: list[str]) -> dict[str, list[str]]:
        """Describe how the function uses each requested fixture value."""
        parents = {
            id(child): parent
            for parent in ast.walk(fn)
            for child in ast.iter_child_nodes(parent)
        }
        usage: dict[str, list[str]] = {a: [] for a in args}
        for node in ast.walk(fn):
            if not (isinstance(node, ast.Name) and node.id in usage):
                continue
            parent = parents.get(id(node))
            if (
                isinstance(parent, (ast.If, ast.While, ast.IfExp))
                and parent.test is node
            ):
                how = "condition"
            elif isinstance(parent, (ast.BoolOp, ast.UnaryOp, ast.Compare)):
                how = "condition"
            elif isinstance(parent, ast.Assign) and any(
                isinstance(t, ast.Subscript) for t in parent.targets
            ):
                target = next(t for t in parent.targets if isinstance(t, ast.Subscript))
                how = f"stored in {dotted(target.value) or 'a container'}[...]"
            elif isinstance(parent, ast.Call) and node is not parent.func:
                how = f"passed to {dotted(parent.func) or 'a call'}()"
            elif isinstance(parent, ast.Attribute):
                how = f"attribute .{parent.attr}"
            elif isinstance(parent, (ast.For, ast.comprehension)):
                how = "iterated"
            elif isinstance(parent, (ast.Return, ast.Yield)):
                how = "returned"
            elif isinstance(parent, ast.FormattedValue):
                how = "formatted into a string"
            else:
                how = type(parent).__name__.lower() if parent else "unknown"
            if how not in usage[node.id]:
                usage[node.id].append(how)
        return usage

    @staticmethod
    def _requested_args(fn, method=False) -> list[str]:
        a = fn.args
        positional = a.posonlyargs + a.args
        if method and positional:
            positional = positional[1:]
        n_defaults = len(a.defaults)
        names = [p.arg for p in positional[: len(positional) - n_defaults]]
        names += [k.arg for k, d in zip(a.kwonlyargs, a.kw_defaults) if d is None]
        return names

    def fingerprint(self, fn) -> str:
        """Hash of the code, args and the same-module helpers/constants it uses."""
        parts = [
            ",".join(self._requested_args(fn)),
            *(ast.dump(d) for d in fn.decorator_list),
            ast.dump(ast.Module(body=_strip_docstring(fn.body), type_ignores=[])),
        ]
        seen = set()
        stack = [fn]
        while stack:
            current = stack.pop()
            shadowed = local_names(current)
            for n in ast.walk(current):
                if (
                    isinstance(n, ast.Name)
                    and n.id not in seen
                    and n.id not in shadowed
                ):
                    seen.add(n.id)
                    if (
                        n.id in self.functions
                        and self.functions[n.id] is not fn
                        and n.id not in self.fixture_funcs
                    ):
                        parts.append(ast.dump(self.functions[n.id]))
                        stack.append(self.functions[n.id])
                    elif n.id in self.constants:
                        parts.append(ast.dump(self.constants[n.id]))
                    elif n.id in self.imports:
                        parts.append("import:" + "/".join(self.imports[n.id]))
        return hashlib.sha1("\n".join(parts).encode()).hexdigest()[:12]

    def _mark_info(self, decorators):
        """Return (markers, usefixtures, direct_params, indirect_params)."""
        markers, usefix, direct, indirect = [], [], set(), set()
        for dec in decorators:
            target = dec.func if isinstance(dec, ast.Call) else dec
            name = dotted(target) or ""
            if ".mark." not in f".{name}":
                continue
            mark = name.split("mark.", 1)[1]
            markers.append(self._finding("marker", "used", mark, dec))
            if not isinstance(dec, ast.Call):
                continue
            if mark == "usefixtures":
                for a in dec.args:
                    usefix.extend(literal_strs(a) or [])
            elif mark == "parametrize" and dec.args:
                names = literal_strs(dec.args[0]) or []
                if len(names) == 1:
                    names = [n.strip() for n in names[0].split(",")]
                ind = next((k.value for k in dec.keywords if k.arg == "indirect"), None)
                if isinstance(ind, ast.Constant) and ind.value is True:
                    indirect.update(names)
                elif ind is not None and (ind_names := literal_strs(ind)):
                    indirect.update(ind_names)
                    direct.update(n for n in names if n not in ind_names)
                else:
                    direct.update(names)
        return markers, usefix, direct, indirect

    def _pytestmark_decorators(self):
        for node in self.tree.body:
            if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "pytestmark" for t in node.targets
            ):
                v = node.value
                return list(v.elts) if isinstance(v, (ast.List, ast.Tuple)) else [v]
        return []

    def _test_item(self, fn, container, inherited_decorators) -> TestItem:
        markers, usefix, direct, _ = self._mark_info(
            inherited_decorators + fn.decorator_list
        )
        args = [
            a
            for a in self._requested_args(fn, method=bool(container))
            if a not in direct
        ]
        return TestItem(
            name=fn.name,
            file=self.rel,
            line=fn.lineno,
            suite=self.suite,
            args=args,
            usefixtures=usefix,
            container=container,
            params=sorted(direct),
            markers=markers,
            facts=self.collect_facts(fn),
        )

    def parse(self, collect_tests: bool) -> ModuleInfo:
        info = ModuleInfo(
            rel=self.rel, kind=self.kind, origin=self.origin, suite=self.suite
        )
        module_marks = self._pytestmark_decorators()
        for node in ast.walk(self.tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                info.imports.extend(
                    f for f in self.collect_facts(node) if f.category == "import"
                )
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                self._module_call(node, info)
        defs = (ast.FunctionDef, ast.AsyncFunctionDef)
        for node in self.tree.body:
            if isinstance(node, defs):
                fixture = self._fixture_def(node)
                if fixture:
                    info.fixtures.append(fixture)
                elif node.name.startswith("pytest_"):
                    info.hooks.append(
                        Hook(
                            node.name,
                            self.rel,
                            node.lineno,
                            self.origin,
                            self.collect_facts(node),
                        )
                    )
                    info.generates_tests |= node.name == "pytest_generate_tests"
                elif collect_tests and _matches(node.name, self.python_functions):
                    info.tests.append(self._test_item(node, None, module_marks))
            elif isinstance(node, ast.ClassDef):
                self._parse_class(node, info, collect_tests, module_marks)
            elif isinstance(node, (ast.Assign, ast.AnnAssign, ast.Expr, ast.If)):
                if isinstance(node, ast.Assign) and any(
                    isinstance(t, ast.Name) and t.id == "pytest_plugins"
                    for t in node.targets
                ):
                    values = literal_strs(node.value)
                    for v in values or ["<expr>"]:
                        info.pytest_plugins.append(
                            self._finding("plugin", "pytest_plugins", v, node)
                        )
                info.facts.extend(
                    f
                    for f in self.collect_facts(node, visited=set(self.constants))
                    if f.category != "import"
                )
        return info

    def _parse_class(self, node: ast.ClassDef, info, collect_tests, module_marks):
        is_test_class = collect_tests and _matches(node.name, self.python_classes)
        level = "class" if is_test_class else self.level
        if not is_test_class and self.kind != "plugin":
            return
        for item in node.body:
            if not isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            fixture = self._fixture_def(item, container=node.name, level=level)
            if fixture:
                info.fixtures.append(fixture)
            elif is_test_class and _matches(item.name, self.python_functions):
                info.tests.append(
                    self._test_item(item, node.name, module_marks + node.decorator_list)
                )

    def _module_call(self, node: ast.Call, info: ModuleInfo):
        attr = node.func.attr
        if attr in ("addoption", "_addoption"):
            for a in node.args:
                s = literal_str(a)
                if s and s.startswith("-"):
                    info.options_defined.append(
                        self._finding("cli_option", "defined", s, node)
                    )
            for kw in node.keywords:
                if kw.arg == "dest" and (s := literal_str(kw.value)):
                    info.options_defined.append(
                        self._finding("cli_option", "dest", s, node)
                    )
        elif attr == "addinivalue_line" and len(node.args) >= 2:
            if literal_str(node.args[0]) == "markers" and (
                s := literal_str(node.args[1])
            ):
                name = re.split(r"[:(]", s, maxsplit=1)[0].strip()
                info.markers_registered.append(
                    self._finding("marker", "registered", name, node)
                )


def parse_module(source: str, rel: str, *, collect_tests=False, **kwargs) -> ModuleInfo:
    """Parse one module; a syntax error is recorded instead of raised."""
    try:
        return ModuleParser(source, rel, **kwargs).parse(collect_tests)
    except SyntaxError as e:
        return ModuleInfo(
            rel=rel,
            kind=kwargs.get("kind", "?"),
            origin=kwargs.get("origin", "?"),
            suite=kwargs.get("suite"),
            parse_error=f"{e.msg} (line {e.lineno})",
        )
