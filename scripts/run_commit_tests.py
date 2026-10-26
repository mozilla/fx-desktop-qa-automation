import re
import sys
from pathlib import Path
from subprocess import CalledProcessError, check_output

from manifests.testkey import TestKey
from modules.fxa_token import LOGIN_COMMAND

TEST_RE = re.compile(r"tests/.*test\w+\.py")
MOCK_SERVER_CODE_RE = re.compile(
    r"modules/(mock_server|classes/recording|browser_object_smart_\w+)\.py"
    r"|modules/data/smart_\w+\.components\.json"
    r"|tests/smart_window/conftest\.py"
)


def uses_mock_server(test: str) -> bool:
    return bool(
        re.search(
            r"\b(smart_window_chat|mock_server)\b",
            Path(test).read_text(encoding="utf-8"),
        )
    )


def has_recording(test: str) -> bool:
    """Tests that build their replies with modules.classes.recording need none."""
    path = Path(test)
    folder = Path("data", "recordings", path.parent.name)
    return (
        "modules.classes.recording" in path.read_text(encoding="utf-8")
        or (folder / f"{path.stem}.json").exists()
        or (folder / path.stem).is_dir()
    )


if __name__ == "__main__":
    manifest = TestKey("manifests/key.yaml")
    committed_files = (
        check_output(
            ["git", "--no-pager", "diff", "--name-only", "--cached", "--diff-filter=d"]
        )
        .decode()
        .splitlines()
    )

    tests = [f for f in committed_files if TEST_RE.match(f)]
    if any(MOCK_SERVER_CODE_RE.match(f) for f in committed_files):
        suite_tests = [
            t.as_posix()
            for t in sorted(Path("tests", "smart_window").glob("test_*.py"))
        ]
        tests += [t for t in suite_tests if t not in tests and uses_mock_server(t)]

    missing = [t for t in tests if uses_mock_server(t) and not has_recording(t)]
    if missing:
        print(
            "No recording yet. Record it, after signing in once with "
            f"{LOGIN_COMMAND} (see SMART_WINDOW_MOCK_SERVER.md):"
        )
        for test in missing:
            print(f'  pytest "{test}" --mock-mode=record')
        sys.exit(1)

    tests = manifest.filter_filenames_by_pass(tests, assume_pass=True)

    if tests:
        print(f"Testing {tests} ...")

        try:
            print(
                "\n".join(
                    check_output(
                        [
                            "pytest",
                            "--run-headless",
                            "-m",
                            "not unstable and not headed",
                            "-n",
                            "4",
                            *tests,
                        ]
                    )
                    .decode()
                    .splitlines()
                )
            )
        except CalledProcessError as exc:
            error_lines = "\n".join(exc.output.decode().splitlines())
            print("Error", exc.returncode)
            print(error_lines)
            # pass if no files are runnable
            if exc.returncode != 5:
                sys.exit(1)
