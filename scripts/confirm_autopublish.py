import sys
from datetime import UTC, datetime, timedelta
from subprocess import check_output


def main():
    check_output("git fetch origin nightly".split(" "))
    tags = check_output("git ls-remote --tags origin".split(" ")).decode()
    now = datetime.now(UTC)
    for tag in tags:
        sha = tag.split(" ")[0]
        commit_date_string = check_output(
            ["git", "--no-pager", "log", "-1", "--format=%cI", sha]
        ).decode()
        commit_dt = datetime.fromisoformat(commit_date_string)
        if now - commit_dt < timedelta(days=14.0):
            print(True)
            sys.exit(1)
    print(False)
    sys.exit(0)


if __name__ == "__main__":
    main()
