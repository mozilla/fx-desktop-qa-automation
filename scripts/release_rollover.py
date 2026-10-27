"""Archive beta as fx<major>, then point beta at nightly on release day."""

import argparse
import json
import logging
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

SCHEDULE_URL = "https://whattrainisitnow.com/api/release/schedule/"
LOG = logging.getLogger(__name__)


def positive_major(value: str) -> int:
    if not re.fullmatch(r"[1-9][0-9]*", value):
        raise argparse.ArgumentTypeError("Expected a positive major version, e.g. 159")
    return int(value)


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], check=True, text=True, capture_output=True
    ).stdout.strip()


def report(message: str) -> None:
    LOG.info(message)
    if summary := os.environ.get("GITHUB_STEP_SUMMARY"):
        with Path(summary).open("a", encoding="utf-8") as file:
            file.write(message + "\n\n")


def fetch_schedule(version: int | None) -> dict:
    query = f"{version}.0" if version is not None else "release"
    request = Request(
        f"{SCHEDULE_URL}?version={query}",
        headers={"Accept": "application/json", "User-Agent": "Firefox-QA-rollover"},
    )
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def parse_schedule(data: dict) -> tuple[int, datetime]:
    # Reject dot releases: only a major release may start a new beta cycle.
    match = re.fullmatch(r"([1-9][0-9]*)\.0", str(data.get("version", "")))
    if not match:
        raise ValueError("API version must be a major release, e.g. 159.0")
    released_at = datetime.fromisoformat(data["release"])
    if released_at.tzinfo is None:
        raise ValueError("API release timestamp must include a timezone")
    return int(match[1]), released_at.astimezone(timezone.utc)


def rollover(
    data: dict,
    first_version: int,
    dry_run: bool,
    requested_version: int | None = None,
    now: datetime | None = None,
) -> None:
    version, released_at = parse_schedule(data)
    if requested_version is not None and version != requested_version:
        raise ValueError("API returned a different version than requested")
    if version < first_version:
        report(
            f"Skipped Firefox {version}: first automated version is {first_version}."
        )
        return
    if (now or datetime.now(timezone.utc)) < released_at:
        report(
            f"Skipped Firefox {version}: release is scheduled for {released_at.isoformat()}."
        )
        return

    archive = f"refs/heads/fx{version}"
    # A completed atomic rollover creates this archive; retries must skip it.
    if git("ls-remote", "--heads", "origin", archive):
        report(f"Skipped Firefox {version}: fx{version} already exists.")
        return

    git(
        "fetch",
        "--no-tags",
        "origin",
        "+refs/heads/beta:refs/remotes/origin/beta",
        "+refs/heads/nightly:refs/remotes/origin/nightly",
    )
    beta_sha = git("rev-parse", "refs/remotes/origin/beta")
    nightly_sha = git("rev-parse", "refs/remotes/origin/nightly")
    report(
        f"Firefox {version}: archive beta `{beta_sha}` as `fx{version}`; "
        f"update beta to nightly `{nightly_sha}`. Dry run: {dry_run}."
    )
    command = [
        "push",
        "--atomic",
        f"--force-with-lease={archive}:",
        f"--force-with-lease=refs/heads/beta:{beta_sha}",
    ]
    if dry_run:
        command.append("--dry-run")
    # Both updates succeed together.
    command.extend(
        [
            "origin",
            f"{beta_sha}:{archive}",
            f"{nightly_sha}:refs/heads/beta",
        ]
    )
    git(*command)
    report(
        "Preview complete; branches were not changed."
        if dry_run
        else "Rollover complete."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--first-release-version",
        type=positive_major,
        default=os.environ.get("FIRST_RELEASE_VERSION") or None,
    )
    parser.add_argument(
        "--release-version",
        type=positive_major,
        default=os.environ.get("RELEASE_VERSION") or None,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=os.environ.get("DRY_RUN", "false").lower() == "true",
    )
    args = parser.parse_args()
    if args.first_release_version is None:
        parser.error("Set FIRST_RELEASE_VERSION or pass --first-release-version")
    try:
        rollover(
            fetch_schedule(args.release_version),
            args.first_release_version,
            args.dry_run,
            args.release_version,
        )
    except subprocess.CalledProcessError as error:
        LOG.error("Git operation failed: %s", error.stderr.strip())
        raise SystemExit(1) from error
    except Exception as error:
        LOG.error("Rollover failed: %s", error)
        raise SystemExit(1) from error


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    main()
