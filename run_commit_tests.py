import sys
from subprocess import CalledProcessError, check_output

if __name__ == "__main__":
    committed_files = (
        check_output(["git", "--no-pager", "diff", "--name-only", "--cached"])
        .decode()
        .splitlines()
    )

    tests = [f for f in committed_files if f.startswith("test") and f.endswith(".py")]

    if tests:
        print(f"Testing {tests} ...")

        try:
            print(
                "\n".join(
                    check_output(
                        ["pytest", "--run-headless", "-m", "not unstable", *tests]
                    )
                    .decode()
                    .splitlines()
                )
            )
        except CalledProcessError as exc:
            error_lines = "\n".join(exc.output.decode().splitlines())
            print("Error", exc.returncode)
            print(error_lines)
            sys.exit(1)
