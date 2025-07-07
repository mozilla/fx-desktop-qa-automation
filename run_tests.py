import argparse
import os
import platform
import sys

import pytest

LINUX_FX_EXEC = "./firefox/firefox"
WIN_FX_EXEC = "C:\\Program Files\\Custom Firefox\\firefox.exe"
MAC_FX_EXEC = ""


def run_suite(parsed_args):
    """Convert script / argparse args (parsed_args) to pytest_args"""
    pytest_args = parsed_args.added_args or []
    if "--ci" in pytest_args and "--fx-executable" not in pytest_args:
        fx_exec = LINUX_FX_EXEC
        if platform.system().lower().startswith("win"):
            fx_exec = WIN_FX_EXEC
        elif platform.system().lower().startswith("darwin"):
            fx_exec = MAC_FX_EXEC
        pytest_args.extend(["--fx-executable", fx_exec])
    if parsed_args.pyproject:
        os.rename(parsed_args.pyproject, "pyproject.toml")
    if parsed_args.subset:
        tests = open("selected_tests").read()
    else:
        tests = "tests"
    workers = None
    if not parsed_args.headed:
        workers = "auto"
        pytest_args.append("--run-headless")
    if parsed_args.workers:
        workers = pytest_args.workers
    if workers:
        pytest_args.extend(["-n", workers])
    pytest_args.extend(tests.split())
    return pytest.main(pytest_args)


parser = argparse.ArgumentParser(
    prog="Run STARfox tests", description="Run the STARfox suites"
)

parser.add_argument("added_args", nargs="*")
parser.add_argument("--pyproject", default=None)
parser.add_argument("-w", "--workers", default=None)
parser.add_argument("-s", "--subset", action="store_true")
parser.add_argument("--headed", action="store_true")

sys.exit(run_suite(parser.parse_args()))
