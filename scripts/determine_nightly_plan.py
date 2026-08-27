from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict, dataclass
from datetime import date, datetime, timezone
from pathlib import Path


CYCLE_LENGTH_DAYS = 14
FULL_TEST_SETS = ("smoke", "functional", "glean")


@dataclass(frozen=True)
class NightlyPlan:
    should_run: bool
    test_sets: list[str]
    cycle_day: int
    reason: str
    build_date: str
    build_hour: int
    first_thursday_cycle_day: int


def parse_utc_datetime(value: str) -> datetime:
    """Parse a Firefox build ID or an ISO-8601 UTC timestamp."""

    if not value:
        raise ValueError("build_datetime_utc is required.")

    value = value.strip()

    if value.startswith("buildID="):
        value = value.removeprefix("buildID=")

    # Firefox build ID format: YYYYMMDDHHMMSS
    if len(value) == 14 and value.isdigit():
        try:
            parsed = datetime.strptime(value, "%Y%m%d%H%M%S")
        except ValueError as error:
            raise ValueError(
                f"Invalid Firefox build ID: {value}"
            ) from error

        return parsed.replace(tzinfo=timezone.utc)

    # ISO-8601 UTC format: YYYY-MM-DDTHH:MM:SSZ
    if not value.endswith("Z"):
        raise ValueError(
            "Build time must be a 14-digit Firefox build ID or "
            "an ISO-8601 UTC timestamp ending in Z."
        )

    try:
        parsed = datetime.fromisoformat(f"{value[:-1]}+00:00")
    except ValueError as error:
        raise ValueError(
            f"Invalid UTC build timestamp: {value}"
        ) from error

    return parsed.astimezone(timezone.utc)


def parse_anchor_date(value: str) -> date:
    """Parse the first UTC date of a known 14-day release cycle."""

    if not value:
        raise ValueError(
            "Repository variable RELEASE_CYCLE_ANCHOR_UTC is not set."
        )

    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise ValueError(
            "RELEASE_CYCLE_ANCHOR_UTC must use YYYY-MM-DD."
        ) from error


def parse_test_sets(value: str) -> list[str]:
    """Validate and parse the default test-set JSON array."""

    try:
        test_sets = json.loads(value)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"test_sets must be valid JSON: {error.msg}"
        ) from error

    if (
        not isinstance(test_sets, list)
        or not test_sets
        or not all(
            isinstance(test_set, str) and test_set.strip()
            for test_set in test_sets
        )
    ):
        raise ValueError(
            "test_sets must be a non-empty JSON array of non-empty strings."
        )

    return test_sets


def determine_plan(
    *,
    build_datetime: datetime,
    release_cycle_anchor: date,
    default_test_sets: list[str],
    morning_cutoff_hour: int,
) -> NightlyPlan:
    """Calculate the nightly test plan."""

    if not 0 <= morning_cutoff_hour < 24:
        raise ValueError(
            "morning_cutoff_hour_utc must be between 0 and 23."
        )

    elapsed_days = (build_datetime.date() - release_cycle_anchor).days

    if elapsed_days < 0:
        raise ValueError(
            "Build time precedes RELEASE_CYCLE_ANCHOR_UTC."
        )

    # cycle_index is zero-based:
    #   0  = first day
    #   13 = last day
    cycle_index = elapsed_days % CYCLE_LENGTH_DAYS
    cycle_day = cycle_index + 1

    # date.weekday() uses Monday=0 through Sunday=6.
    # Thursday therefore has index 3.
    first_thursday_index = (3 - release_cycle_anchor.weekday()) % 7
    first_thursday_cycle_day = first_thursday_index + 1

    should_run = build_datetime.hour < morning_cutoff_hour
    test_sets: list[str] = []
    reason = "afternoon build"

    if should_run:
        test_sets = default_test_sets.copy()
        reason = "ordinary morning build"

        if cycle_index == 0:
            test_sets = list(FULL_TEST_SETS)
            reason = "first day of release cycle"
        elif cycle_index == CYCLE_LENGTH_DAYS - 1:
            test_sets = list(FULL_TEST_SETS)
            reason = "last day of release cycle"
        elif cycle_index == first_thursday_index:
            test_sets = list(FULL_TEST_SETS)
            reason = "first Thursday of release cycle"

    return NightlyPlan(
        should_run=should_run,
        test_sets=test_sets,
        cycle_day=cycle_day,
        reason=reason,
        build_date=build_datetime.date().isoformat(),
        build_hour=build_datetime.hour,
        first_thursday_cycle_day=first_thursday_cycle_day,
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


def write_github_summary(
    plan: NightlyPlan,
    build_datetime_utc: str,
) -> None:
    """Add the calculated plan to the GitHub Actions job summary."""

    github_summary = os.environ.get("GITHUB_STEP_SUMMARY")

    if not github_summary:
        return

    test_sets_json = json.dumps(plan.test_sets, separators=(",", ":"))

    append_lines(
        github_summary,
        [
            "### Nightly test plan",
            "",
            "| Setting | Value |",
            "|---|---|",
            f"| Build timestamp | `{build_datetime_utc}` |",
            f"| Build UTC date | `{plan.build_date}` |",
            f"| Build UTC hour | `{plan.build_hour}` |",
            f"| Cycle day | `{plan.cycle_day} of {CYCLE_LENGTH_DAYS}` |",
            (
                "| First Thursday cycle day | "
                f"`{plan.first_thursday_cycle_day}` |"
            ),
            f"| Run tests | `{str(plan.should_run).lower()}` |",
            f"| Test sets | `{test_sets_json}` |",
            f"| Reason | {plan.reason} |",
        ],
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Determine the test plan for a Firefox nightly build."
    )
    parser.add_argument(
        "--build-datetime-utc",
        required=True,
        help=(
            "Firefox build ID or UTC timestamp, such as "
            "20260818174224, buildID=20260818174224, or "
            "2026-08-18T17:42:24Z."
        ),
    )
    parser.add_argument(
        "--release-cycle-anchor-utc",
        required=True,
        help="UTC date of a known cycle day 1, using YYYY-MM-DD.",
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
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        plan = determine_plan(
            build_datetime=parse_utc_datetime(
                args.build_datetime_utc
            ),
            release_cycle_anchor=parse_anchor_date(
                args.release_cycle_anchor_utc
            ),
            default_test_sets=parse_test_sets(
                args.default_test_sets
            ),
            morning_cutoff_hour=args.morning_cutoff_hour_utc,
        )
    except ValueError as error:
        print(f"::error::{error}", file=sys.stderr)
        return 1

    write_github_outputs(plan)
    write_github_summary(plan, args.build_datetime_utc)

    # This is for when running the script locally.
    print(json.dumps(asdict(plan), indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
