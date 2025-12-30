import re
import sys
from subprocess import CalledProcessError, check_output

TEST_RE = re.compile(r"tests/.*test\w+\.py")

if __name__ == "__main__":
    committed_files = (
        check_output(["git", "--no-pager", "diff", "--name-only", "--cached"])
        .decode()
        .splitlines()
    )

    tests = [f for f in committed_files if TEST_RE.match(f)]

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
