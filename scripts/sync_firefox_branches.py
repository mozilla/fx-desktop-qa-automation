"""Archive main as release<major>, point main at nightly and prune old release branches."""

import argparse
import json
import os
import re
import subprocess
from pathlib import Path
from urllib.request import Request, urlopen

SCHEDULE_URL = "https://whattrainisitnow.com/api/release/schedule/?version=release"
RELEASE_REF = re.compile(r"refs/heads/release([1-9][0-9]*)")


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], check=True, text=True, capture_output=True
    ).stdout.strip()


def summarize(text: str) -> None:
    print(text)
    if summary := os.environ.get("GITHUB_STEP_SUMMARY"):
        with Path(summary).open("a", encoding="utf-8") as file:
            file.write(text + "\n\n")


def positive_int(value: str) -> int:
    if not re.fullmatch(r"[1-9][0-9]*", value):
        raise argparse.ArgumentTypeError("expected a positive integer")
    return int(value)


def current_release_major() -> int:
    """Return the major version of the current Firefox release."""
    request = Request(SCHEDULE_URL, headers={"User-Agent": "fx-desktop-qa-automation"})
    with urlopen(request, timeout=30) as response:
        version = json.load(response)["version"]
    if not (match := re.fullmatch(r"([1-9][0-9]*)\.0", version)):
        raise SystemExit(f"Unexpected release version from the schedule: {version}")
    return int(match[1])


def open_prs_on_main() -> str:
    try:
        output = subprocess.run(
            ["gh", "pr", "list", "--base", "main", "--state", "open"]
            + ["--limit", "1000", "--json", "number,title,author"],
            check=True,
            text=True,
            capture_output=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        print("::warning::Could not list open pull requests targeting main.")
        return "Could not list them."
    prs = json.loads(output)
    return (
        "\n".join(
            f"- #{pr['number']} {pr['title']} (@{pr['author']['login']})" for pr in prs
        )
        or "None."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--released-major",
        type=positive_int,
        default=os.environ.get("RELEASED_MAJOR") or None,
        help="Major version on main; defaults to the current Firefox release",
    )
    parser.add_argument(
        "--retention",
        type=positive_int,
        default=os.environ.get("RETENTION") or "2",
        help="Number of release branches to keep",
    )
    parser.add_argument(
        "--first-release-version",
        type=positive_int,
        default=os.environ.get("FIRST_RELEASE_VERSION") or None,
        help="First major to promote; checks the version before any releaseNNN exists",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=os.environ.get("DRY_RUN", "true").lower() == "true",
    )
    args = parser.parse_args()
    major = args.released_major or current_release_major()

    git(
        "fetch",
        "--no-tags",
        "origin",
        "+refs/heads/main:refs/remotes/origin/main",
        "+refs/heads/nightly:refs/remotes/origin/nightly",
    )
    main_sha = git("rev-parse", "refs/remotes/origin/main")
    nightly_sha = git("rev-parse", "refs/remotes/origin/nightly")
    releases = {}
    for line in git(
        "ls-remote", "--heads", "origin", "refs/heads/release*"
    ).splitlines():
        sha, ref = line.split()
        if match := RELEASE_REF.fullmatch(ref):
            releases[int(match[1])] = sha

    if not releases:
        if args.first_release_version is None:
            raise SystemExit("No releaseNNN branch yet: set FIRST_RELEASE_VERSION.")
        if major < args.first_release_version:
            summarize(
                f"Skipped Firefox {major}: automation starts at "
                f"{args.first_release_version}."
            )
            return

    promote = major not in releases
    # main is always one train ahead of the newest release branch.
    expected = max(releases) + 1 if releases else args.first_release_version
    if promote and major != expected:
        raise SystemExit(
            f"Expected release{expected}, got release{major}. "
            "Refusing a stale or out-of-order promotion."
        )

    refspecs, leases = [], []
    if promote:
        refspecs += [
            f"{main_sha}:refs/heads/release{major}",
            f"{nightly_sha}:refs/heads/main",
        ]
        leases += [
            f"--force-with-lease=refs/heads/release{major}:",
            f"--force-with-lease=refs/heads/main:{main_sha}",
        ]
    old = sorted(releases.keys() | {major}, reverse=True)[args.retention :]
    for version in old:
        refspecs.append(f":refs/heads/release{version}")
        leases.append(
            f"--force-with-lease=refs/heads/release{version}:{releases[version]}"
        )

    summarize(
        "### Firefox train promotion\n\n"
        f"- Result: `{'promote' if promote else 'already-promoted'}`\n"
        f"- Release branch: `release{major}`\n"
        f"- Main SHA at start: `{main_sha}`\n"
        f"- Nightly SHA at start: `{nightly_sha}`\n"
        f"- Release branches to delete: {', '.join(f'`release{v}`' for v in old) or 'none'}\n"
        f"- Dry run: `{str(args.dry_run).lower()}`"
    )
    if promote:
        summarize(
            "### Open pull requests targeting main\n\n"
            "A live promotion changes the commit behind main for these pull requests.\n\n"
            + open_prs_on_main()
        )
    if args.dry_run or not refspecs:
        summarize("No branches were changed.")
        return
    # One atomic transaction: a failed lease or ref update changes nothing.
    git("push", "--atomic", *leases, "origin", *refspecs)
    summarize("Branches updated.")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as error:
        raise SystemExit(f"git failed: {error.stderr.strip()}") from error
