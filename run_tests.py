import argparse
import os
import platform
import sys
from pathlib import Path
from subprocess import check_output

import mozinstall
import pytest
import requests

LINUX_FX_EXEC = "./firefox/firefox"
WIN_FX_EXEC = "C:\\Program Files\\Custom Firefox\\firefox.exe"
MAC_FX_EXEC = ""


def get_fx_exec():
    fx_exec = LINUX_FX_EXEC
    if platform.system().lower().startswith("win"):
        fx_exec = WIN_FX_EXEC
    elif platform.system().lower().startswith("darwin"):
        fx_exec = MAC_FX_EXEC
    return fx_exec


def install():
    command = ["python", "collect_executables.py"]
    if not platform.system().lower().startswith("win"):
        command = ["./collect_executables.sh"]
    target_filename = "setup.exe"
    if platform.system().lower().startswith("darwin"):
        target_filename = "Firefox.dmg"
    elif platform.system().lower().startswith("linux"):
        target_filename = "firefox.tar.xz"
    url = check_output(command).decode()
    if "collect_executables.py" in command:
        resp = requests.get(url)
        resp.raise_for_status()
        with open(target_filename, "wb") as fh:
            fh.write(resp.content)
        mozinstall.install(target_filename, Path(get_fx_exec()).parent)


def run_suite(parsed_args):
    """Convert script / argparse args (parsed_args) to pytest_args"""
    pytest_args = parsed_args.added_args or []
    if parsed_args.install:
        install()
    if parsed_args.ci and "--fx-executable" not in pytest_args:
        pytest_args.extend(["--fx-executable", get_fx_exec()])
    if parsed_args.pyproject:
        os.replace(parsed_args.pyproject, "pyproject.toml")
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
    print("pytest " + " ".join(pytest_args))
    return pytest.main(pytest_args)


parser = argparse.ArgumentParser(
    prog="Run STARfox tests", description="Run the STARfox suites"
)

parser.add_argument("added_args", nargs="*")
parser.add_argument("--pyproject", default=None)
parser.add_argument("-w", "--workers", default=None)
parser.add_argument("-s", "--subset", action="store_true")
parser.add_argument("--install", action="store_true")
parser.add_argument("--ci", action="store_true")
parser.add_argument("--headed", action="store_true")

sys.exit(run_suite(parser.parse_args()))
