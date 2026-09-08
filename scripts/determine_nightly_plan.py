from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

FULL_TEST_SETS = ("smoke", "nightly")

# Firefox Release Management's schedule API.
SCHEDULE_URL = "https://whattrainisitnow.com/api/release/schedule/?version=nightly"
SCHEDULE_TIMEOUT_SECONDS = 15

# Fallback for when the schedule API cannot be read: count 14-day cycles from a
# known first day of a cycle, which is set as a repository variable.
ANCHOR_ENV_VAR = "RELEASE_CYCLE_ANCHOR_UTC"
CYCLE_LENGTH_DAYS = 14


@dataclass(frozen=True)
class ReleaseCycle:
    version: str
    start: date
    merge_day: date
    source: str


@dataclass(frozen=True)
class NightlyPlan:
    should_run: bool
    test_sets: list[str]
    cycle_day: int
    cycle_length: int
    reason: str
    build_date: str
    build_hour: int
    nightly_version: str
    cycle_start: str
    cycle_source: str


def parse_build_datetime(value: str) -> datetime:
    """Parse the UTC build time from a target_info value: buildID=YYYYMMDDHHMMSS."""

    build_id = value.strip().removeprefix("buildID=")

    try:
        parsed = datetime.strptime(build_id, "%Y%m%d%H%M%S")
    except ValueError as error:
        raise ValueError(
            f"target_info must use buildID=YYYYMMDDHHMMSS, got: {value}"
        ) from error

    return parsed.replace(tzinfo=timezone.utc)


def parse_test_sets(value: str) -> list[str]:
    """Validate and parse the default test-set JSON array."""

    try:
        test_sets = json.loads(value)
    except json.JSONDecodeError as error:
        raise ValueError(f"test_sets must be valid JSON: {error.msg}") from error

    if (
        not isinstance(test_sets, list)
        or not test_sets
        or not all(
            isinstance(test_set, str) and test_set.strip() for test_set in test_sets
        )
    ):
        raise ValueError(
            "test_sets must be a non-empty JSON array of non-empty strings."
        )

    return test_sets


def fetch_train_info(url: str) -> ReleaseCycle:
    """Read the current Nightly cycle from the Firefox release schedule API."""

    request = urllib.request.Request(url, headers={"Accept": "application/json"})

    with urllib.request.urlopen(request, timeout=SCHEDULE_TIMEOUT_SECONDS) as response:
        schedule = json.load(response)

    try:
        return ReleaseCycle(
            version=str(schedule["version"]),
            start=datetime.fromisoformat(schedule["nightly_start"]).date(),
            merge_day=datetime.fromisoformat(schedule["merge_day"]).date(),
            source="release schedule API",
        )
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError(f"Unexpected release schedule payload: {error}") from error


def parse_anchor_date(value: str) -> date:
    """Parse the first UTC date of a known 14-day release cycle."""

    if not value:
        raise ValueError(f"Repository variable {ANCHOR_ENV_VAR} is not set.")

    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise ValueError(f"{ANCHOR_ENV_VAR} must use YYYY-MM-DD.") from error


def calculate_from_anchor(anchor: date, build_date: date) -> ReleaseCycle:
    """Derive the cycle around a build date by counting 14-day cycles from an anchor."""

    days_since_anchor = (build_date - anchor).days
    cycles_elapsed = days_since_anchor // CYCLE_LENGTH_DAYS
    cycle_start = anchor + timedelta(days=cycles_elapsed * CYCLE_LENGTH_DAYS)

    return ReleaseCycle(
        version="unknown",
        start=cycle_start,
        merge_day=cycle_start + timedelta(days=CYCLE_LENGTH_DAYS),
        source="Anchor date fallback",
    )


def resolve_release_cycle(
    *, url: str, anchor_value: str, build_date: date
) -> ReleaseCycle:
    """Read the cycle from the schedule API, falling back to the anchor date."""

    try:
        return fetch_train_info(url)
    except (urllib.error.URLError, ValueError) as error:
        print(f"Warning! could not read the release schedule: {error}")

    anchor = parse_anchor_date(anchor_value)
    cycle = calculate_from_anchor(anchor, build_date)
    print(
        f"::warning::Falling back to {CYCLE_LENGTH_DAYS}-day cycles counted from the anchor date"
    )

    return cycle


def determine_plan(
    *,
    build_datetime: datetime,
    cycle: ReleaseCycle,
    default_test_sets: list[str],
    morning_cutoff_hour: int,
) -> NightlyPlan:
    """Calculate the nightly test plan."""

    if not 0 <= morning_cutoff_hour < 24:
        raise ValueError("morning_cutoff_hour_utc must be between 0 and 23.")

    build_date = build_datetime.date()
    should_run = build_datetime.hour < morning_cutoff_hour

    test_sets: list[str] = []
    reason = "afternoon build"

    cycle_day = (build_date - cycle.start).days + 1
    cycle_length = (cycle.merge_day - cycle.start).days

    # date.weekday() uses Monday=0 through Sunday=6, so Thursday is 3.
    first_thursday = cycle.start + timedelta(days=(3 - cycle.start.weekday()) % 7)

    if should_run:
        test_sets = list(default_test_sets)
        reason = "ordinary morning build"

        if build_date == cycle.start:
            test_sets = list(FULL_TEST_SETS)
            reason = "first day of release cycle"
        elif cycle_day == cycle_length:
            test_sets = list(FULL_TEST_SETS)
            reason = "last day of release cycle"
        elif build_date == first_thursday:
            test_sets = list(FULL_TEST_SETS)
            reason = "first Thursday of release cycle"

    return NightlyPlan(
        should_run=should_run,
        test_sets=test_sets,
        cycle_day=cycle_day,
        cycle_length=cycle_length,
        reason=reason,
        build_date=build_date.isoformat(),
        build_hour=build_datetime.hour,
        nightly_version=cycle.version,
        cycle_start=cycle.start.isoformat(),
        cycle_source=cycle.source,
    )


def append_lines(path: str, lines: list[str]) -> None:
    """Append lines to a GitHub Actions environment file."""

    with Path(path).open("a", encoding="utf-8") as output_file:
        for line in lines:
            output_file.write(f"{line}\n")


def write_github_outputs(plan: NightlyPlan) -> None:
    """Write the plan to GITHUB_OUTPUT when running in GitHub Actions."""

    github_output = os.environ.get("GITHUB_OUTPUT")

    if not github_output:
        return

    test_sets_json = json.dumps(plan.test_sets, separators=(",", ":"))

    append_lines(
        github_output,
        [
            f"should_run={str(plan.should_run).lower()}",
            f"test_sets={test_sets_json}",
            f"cycle_day={plan.cycle_day}",
            f"reason={plan.reason}",
        ],
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Determine the test plan for a Firefox nightly build."
    )
    parser.add_argument(
        "--target-info",
        required=True,
        help="Firefox build ID, such as buildID=20260818174224.",
    )
    parser.add_argument(
        "--default-test-sets",
        default='["smoke"]',
        help="JSON array used for ordinary morning builds.",
    )
    parser.add_argument(
        "--morning-cutoff-hour-utc",
        type=int,
        default=12,
        help="Hours before this UTC hour are considered morning.",
    )
    parser.add_argument(
        "--schedule-url",
        default=SCHEDULE_URL,
        help="Firefox release schedule API URL.",
    )
    parser.add_argument(
        "--release-cycle-anchor-utc",
        default=os.environ.get(ANCHOR_ENV_VAR, ""),
        help="UTC date of a known cycle day one, using YYYY-MM-DD.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        build_datetime = parse_build_datetime(args.target_info)
        default_test_sets = parse_test_sets(args.default_test_sets)
    except ValueError as error:
        print(f"Error, {error}", file=sys.stderr)
        return 1

    try:
        cycle = resolve_release_cycle(
            url=args.schedule_url,
            anchor_value=args.release_cycle_anchor_utc,
            build_date=build_datetime.date(),
        )
        plan = determine_plan(
            build_datetime=build_datetime,
            cycle=cycle,
            default_test_sets=default_test_sets,
            morning_cutoff_hour=args.morning_cutoff_hour_utc,
        )
    except ValueError as error:
        print(f"Error, {error}", file=sys.stderr)
        return 1

    write_github_outputs(plan)

    # This is for when running the script locally.
    print(json.dumps(asdict(plan), indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
