"""
Command line entry point.

Example, from the STARfox root:

    python -m scripts.fixture_inventory --repo . --out /tmp/inventory \\
        --firefox-root ~/firefox \\
        --firefox-conftest ~/firefox/testing/dte-ui-test/tests/conftest.py \\
        --firefox-site ~/firefox/python/sites/dte-ui-test.txt \\
        --firefox-site ~/firefox/python/sites/mach.txt \\
        --site-packages .venv/lib/python3.13/site-packages
"""

import argparse
import sys
from pathlib import Path

from .inventory import Inventory, Options
from .report import write_all


def build_parser(
    prog="fixture_inventory",
    description="Read-only report of pytest fixtures and what migrating them needs.",
) -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog=prog, description=description)
    p.add_argument(
        "--repo", type=Path, required=True, help="STARfox checkout to analyse"
    )
    p.add_argument("--tests-dir", default="tests", help="Tests dir, relative to --repo")
    p.add_argument("--out", type=Path, required=True, help="Directory for the reports")
    p.add_argument(
        "--exclude-suite", action="append", default=[], help="Suite to leave out"
    )
    p.add_argument("--firefox-root", type=Path, help="Firefox tree, to shorten paths")
    p.add_argument(
        "--firefox-conftest",
        type=Path,
        action="append",
        default=[],
        help="Firefox conftest that replaces the STARfox root conftest",
    )
    p.add_argument(
        "--firefox-site",
        type=Path,
        action="append",
        default=[],
        help="Firefox python/sites/*.txt file describing the mach virtualenv",
    )
    p.add_argument(
        "--firefox-config",
        type=Path,
        action="append",
        default=[],
        help="Firefox pytest.ini/pyproject.toml, for registered markers",
    )
    p.add_argument(
        "--site-packages",
        type=Path,
        action="append",
        help="site-packages dir to read package metadata and plugin source from "
        "(default: this Python's)",
    )
    return p


def parse_args(argv=None) -> argparse.Namespace:
    return build_parser().parse_args(argv)


def options_from_args(args: argparse.Namespace) -> Options | None:
    """Build inventory Options, or print an error and return None."""
    for path in args.firefox_conftest + args.firefox_site + args.firefox_config:
        if not path.is_file():
            print(f"error: not a file: {path}", file=sys.stderr)
            return None
    return Options(
        repo=args.repo.resolve(),
        tests_dir=args.tests_dir,
        exclude_suites=tuple(args.exclude_suite),
        firefox_conftests=args.firefox_conftest,
        firefox_root=args.firefox_root,
        firefox_sites=args.firefox_site,
        firefox_configs=args.firefox_config,
        site_packages=args.site_packages,
    )


def main(argv=None) -> int:
    args = parse_args(argv)
    out = args.out.resolve()
    opts = options_from_args(args)
    if opts is None:
        return 2
    inventory = Inventory(opts).build()
    for path in write_all(inventory, out):
        print(path)
    s = inventory["summary"]
    print(
        f"{s['tests']} tests, {s['fixture_definitions']} fixture definitions, "
        f"{s['missing_names_after_migration']} names missing after migration"
    )
    return 0
