import argparse
import json
import os
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class NightlyPlan:
    should_run: bool
    reason: str
    build_date: str
    build_hour: int


def parse_build_datetime(value: str) -> datetime:
    """Parse the UTC build time from target_info: buildID=YYYYMMDDHHMMSS."""
    build_id = value.strip().removeprefix("buildID=")

    try:
        if len(build_id) != 14 or not build_id.isascii() or not build_id.isdigit():
            raise ValueError("Build ID must contain exactly 14 digits.")
        parsed = datetime.strptime(build_id, "%Y%m%d%H%M%S")
    except ValueError as error:
        raise ValueError(
            f"target_info must use buildID=YYYYMMDDHHMMSS, got: {value}"
        ) from error

    return parsed.replace(tzinfo=timezone.utc)


def determine_plan(
    *,
    build_datetime: datetime,
    morning_cutoff_hour: int,
) -> NightlyPlan:
    """Select Tuesday and Thursday morning Nightly using the UTC build time."""
    if not 0 <= morning_cutoff_hour < 24:
        raise ValueError("morning_cutoff_hour_utc must be between 0 and 23.")

    build_date = build_datetime.date()
    is_morning = build_datetime.hour < morning_cutoff_hour

    # weekday(): Monday=0, Tuesday=1, Thursday=3, etc.
    should_run = build_date.weekday() in (1, 3) and is_morning
    reason = (
        f"{build_datetime:%A} morning Nightly"
        if should_run
        else "not a selected Nightly build"
    )

    return NightlyPlan(
        should_run=should_run,
        reason=reason,
        build_date=build_date.isoformat(),
        build_hour=build_datetime.hour,
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

    append_lines(
        github_output,
        [
            f"should_run={str(plan.should_run).lower()}",
            # Retained as an empty output for compatibility with the existing YAML.
            "cycle_day=",
            f"reason={plan.reason}",
        ],
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Select Tuesday and Thursday morning Firefox Nightlies."
    )
    parser.add_argument(
        "--target-info",
        required=True,
        help="Firefox build ID, such as buildID=20260818174224.",
    )
    parser.add_argument(
        "--morning-cutoff-hour-utc",
        type=int,
        default=12,
        help="Hours before this UTC hour are considered morning.",
    )
    # The existing YAML still passes this argument; cycle dates are no longer used.
    parser.add_argument(
        "--release-cycle-anchor-utc",
        default="",
        help="Unused compatibility argument for the existing workflow.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        build_datetime = parse_build_datetime(args.target_info)
        plan = determine_plan(
            build_datetime=build_datetime,
            morning_cutoff_hour=args.morning_cutoff_hour_utc,
        )
    except ValueError as error:
        print(f"Error, {error}", file=sys.stderr)
        return 1

    write_github_outputs(plan)

    # Also print the plan for local runs and GitHub Actions logs.
    print(json.dumps(asdict(plan), indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
