import re
import sys
from subprocess import CalledProcessError, check_output

from manifests.testkey import TestKey

TEST_RE = re.compile(r"tests/.*test\w+\.py")

if __name__ == "__main__":
    manifest = TestKey("manifests/key.yaml")
    committed_files = (
        check_output(["git", "--no-pager", "diff", "--name-only", "--cached"])
        .decode()
        .splitlines()
    )

    tests = [f for f in committed_files if TEST_RE.match(f)]
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
