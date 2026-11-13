"""Link bugs to the in-tree and STARfox tests named in their summaries."""

import re
from pathlib import Path

from scripts.bug_test_links.bugzilla import is_intermittent

# A test file path (forward or back slashes, WPT paths start with /), or a bare
# browser_*/test_* file name.
TEST_PATH_RE = re.compile(
    r"(?<![\w/\\.-])("
    r"/?(?:[\w.-]+[/\\])+[\w.-]+\.(?:js|mjs|sjs|html|xhtml|xht|xul|svg|py|toml|ini)"
    r"|(?:browser|test)_[\w.-]+\.(?:js|mjs|html|xhtml|py)"
    r")(?![\w/\\])"
)
# Leading words of a Treeherder-filed summary, e.g. "Intermittent [tier 2] TV".
SUMMARY_PREFIX_RE = re.compile(
    r"^(?:(?:Intermittent|Perma|Frequent|TV|TVW|TEST-UNEXPECTED-\w+|\[[^\]]*\])"
    r"\s*\|?\s+)+"
)
CASE_ID_RE = re.compile(r'def test_case\(\):\s*return "(\d+)"')


def starfox_tests(root: Path = Path("tests")) -> dict[str, dict]:
    """Map each STARfox test file stem and test function name to its file and case."""
    tests = {}
    for path in sorted(root.rglob("test_*.py")):
        text = path.read_text(encoding="utf-8")
        case_id = CASE_ID_RE.search(text)
        test = {
            "path": path.as_posix(),
            "case_id": int(case_id.group(1)) if case_id else None,
        }
        tests[path.stem] = test
        for name in re.findall(r"^def (test_\w+)\(", text, re.MULTILINE):
            tests.setdefault(name, test)
    return tests


def starfox_name_re(tests: dict[str, dict]) -> re.Pattern:
    """Match a STARfox name as a whole token, not as the start of e.g. test_x.js."""
    names = "|".join(sorted(map(re.escape, tests), key=len, reverse=True))
    return re.compile(rf"(?<![\w/\\.])({names})(?:\.py)?(?!\w|\.\w|[/\\])")


def summary_links(bug: dict, tests: dict[str, dict], name_re: re.Pattern) -> list:
    """Return in-tree and STARfox tests named in a bug summary."""
    summary = bug["summary"]
    links = {}
    for match in TEST_PATH_RE.findall(summary):
        path = match.replace("\\", "/")
        test = tests.get(Path(path).stem)
        if test and test["path"].endswith(path):
            links[test["path"]] = ("starfox", "path", test["case_id"])
        else:
            links[path] = ("in_tree", "path", None)

    for name in name_re.findall(summary):
        test = tests[name]
        links.setdefault(test["path"], ("starfox", "path", test["case_id"]))

    # An intermittent naming no test file, e.g. "Intermittent leakcheck | ...";
    # often a harness check or an infra failure rather than one test.
    if not links and is_intermittent(bug):
        label = SUMMARY_PREFIX_RE.sub("", summary).split(" | ")[0].strip()
        if label:
            # A path with no file name, e.g. a tracking bug for browser_foo_*.
            key_type = "path" if "/" in label and " " not in label else "label"
            links[label] = ("in_tree", key_type, None)

    return [
        {
            "bug_id": bug["id"],
            "source": source,
            "test_key": key,
            "test_key_type": key_type,
            "case_id": case_id,
        }
        for key, (source, key_type, case_id) in links.items()
    ]
