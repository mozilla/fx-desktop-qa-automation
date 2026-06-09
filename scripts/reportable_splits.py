"""Print the functional splits that still need coverage for a platform.

Used by both the GitHub (Windows/macOS) and Taskcluster (Linux) functional
pipelines to choose splits by *coverage* instead of by wall-clock hour, so a
build that is only briefly "latest" still gets every split covered on every
platform regardless of when each pipeline happens to fire.

Usage:
    python -m scripts.reportable_splits --platform Windows --format json
    python -m scripts.reportable_splits --platform Linux --format lines --tc-creds
"""

import argparse
import json
import os
import sys

from modules import taskcluster as tc
from modules import testrail_integration as tri


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--platform",
        required=True,
        help="Platform system name: Windows, Darwin, or Linux.",
    )
    parser.add_argument(
        "--format",
        choices=["json", "lines"],
        default="json",
        help="json -> '[\"functional1\"]' (GitHub matrix); lines -> space-separated (bash loop).",
    )
    parser.add_argument(
        "--tc-creds",
        action="store_true",
        help="Fetch TestRail credentials from the Taskcluster secret before querying.",
    )
    args = parser.parse_args(argv)

    if args.tc_creds:
        creds = tc.get_tc_secret()
        if not creds:
            # No creds -> cannot determine coverage; emit nothing so callers no-op.
            print("" if args.format == "lines" else "[]")
            return 0
        os.environ["TESTRAIL_USERNAME"] = creds.get("TESTRAIL_USERNAME")
        os.environ["TESTRAIL_API_KEY"] = creds.get("TESTRAIL_API_KEY")
        os.environ["TESTRAIL_BASE_URL"] = creds.get("TESTRAIL_BASE_URL")

    splits = tri.uncovered_functional_splits(args.platform)

    # stdout must contain ONLY the result; reportable() logs to stderr.
    if args.format == "lines":
        print(" ".join(splits))
    else:
        print(json.dumps(splits))
    return 0


if __name__ == "__main__":
    sys.exit(main())
