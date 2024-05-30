from subprocess import check_output

if __name__ == "__main__":
    committed_files = (
        check_output(["git", "--no-pager", "diff", "--name-only", "--cached"])
        .decode()
        .splitlines()
    )

    tests = [f for f in committed_files if f.startswith("test") and f.endswith(".py")]

    if tests:
        print(f"Testing {tests} ...")

        print(
            "\n".join(
                check_output(["pytest", "--run-headless", *tests]).decode().splitlines()
            )
        )
