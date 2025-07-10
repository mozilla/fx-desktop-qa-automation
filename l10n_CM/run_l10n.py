import logging
import os
import subprocess
import sys
import threading
from contextlib import contextmanager
from http.server import HTTPServer, SimpleHTTPRequestHandler
from json import load

import requests

current_dir = os.path.dirname(__file__)
valid_flags = {"--run-headless", "-n", "--reruns", "--fx-executable", "--ci"}
flag_with_parameter = {"-n", "--reruns"}
valid_region = {"US", "CA", "DE", "FR"}
valid_sites = {
    "demo",
    "amazon",
    "walmart",
    "mediamarkt",
    "lowes",
    "etsy",
    "calvinklein",
    "bestbuy",
    "vans",
    "ebay",
}
live_sites = []

LOCALHOST = "127.0.0.1"
PORT = 8080
os.environ["TEST_EXIT_CODE"] = "0"


class MyHttpRequestHandler(SimpleHTTPRequestHandler):
    live_site = None
    region = None

    def translate_path(self, path):
        """switch the default directory where the html files are served from."""
        base_dir = os.path.join(current_dir, "sites", self.live_site, self.region)
        return os.path.join(base_dir, path.lstrip("/"))

    def log_message(self, format, *args):
        """Remove logs from the server."""
        pass


def start_server(live_site, current_region):
    # set live site attribute
    MyHttpRequestHandler.live_site = live_site
    MyHttpRequestHandler.region = current_region
    # start web server on a separate thread to avoid blocking calls.
    http = HTTPServer((LOCALHOST, PORT), MyHttpRequestHandler)

    thread = threading.Thread(target=lambda: http.serve_forever())
    thread.start()
    return http, thread


@contextmanager
def running_server(live_site, test_region):
    """Context manager to run a server and clean it up automatically."""
    html_path = os.path.join(current_dir, "sites", live_site, test_region)
    if not os.path.exists(html_path):
        raise FileNotFoundError(
            f"Expected HTML directory not found at path: {html_path}"
        )

    httpd, server_thread = start_server(live_site, test_region)
    try:
        yield  # control goes to the caller, server runs in the background
    finally:
        try:
            # Send a dummy request to unblock the server if necessary
            requests.get(f"http://{LOCALHOST}:{PORT}")
        except Exception:
            pass
        httpd.shutdown()
        server_thread.join()
        logging.info(f"{live_site} server shutdown.")


def run_tests(reg, site, flg, all_tests):
    """
    Execute the test suite for a given region with specified flags.

    Args:
        reg (str): The test region identifier.
        site (str): Page being tested.
        flg (list[str]): The list of pytest flags to be used.
        all_tests (list[str]): The list of test file paths to execute.
    """
    all_tests = remove_skipped_tests(all_tests, site, reg)
    try:
        if len(all_tests) > 0:
            logging.info(f"Tests for {reg} region on {site} page.")
            os.environ["CM_SITE"] = site
            os.environ["FX_REGION"] = reg
            subprocess.run(["pytest", *flg, *all_tests], check=True, text=True)
        else:
            logging.info(f"{reg} region on {site} site has no tests.")
    except subprocess.CalledProcessError as e:
        logging.warning(f"Test run failed with exit code: {e.returncode}")
        # true failure instead of run not being reportable.
        if e.returncode != 2:
            if os.environ.get("TEST_EXIT_CODE") == "0":
                with open("TEST_EXIT_CODE", "w") as f:
                    f.write(str(e.returncode))
            os.environ["TEST_EXIT_CODE"] = str(e.returncode)


def get_region_tests(test_region: str) -> list[str]:
    """
    Retrieve the list of test file paths for a specified region.

    Args:
        test_region (str): The region identifier for which tests are retrieved.

    Returns:
        list[str]: A list of test file paths for the given region.
    """
    path_to_region = current_dir + "/region/"
    with open(path_to_region + test_region + ".json", "r") as fp:
        region_data = load(fp)
        raw_tests = region_data.get("tests", [])
        return (
            list(map(lambda test: current_dir + "/Unified/" + test, raw_tests))
            if len(raw_tests) > 0
            else raw_tests
        )


def remove_skipped_tests(extracted_tests, live_site, reg):
    """
    Reads the mapping for the given region and site and removes any tests that are marked as skipped.

    Args:
        extracted_tests (list[str]): The list of test file paths to execute.
        live_site (str): Page being tested.
        reg (str): The test region identifier.
    Returns:
        list[str]: A list of test file paths for the given region.
    """
    mid_path = f"/{reg}/" if live_site != "demo" else "/"
    live_sites = [
        (f"{live_site}{mid_path}{live_site}_{suffix}", f"_{suffix}_")
        for suffix in ("ad", "cc")
    ]
    for live_site, suffix in live_sites:
        skipped_tests = get_skipped_tests(live_site)
        if skipped_tests and skipped_tests != "All":
            skipped_tests = list(
                map(
                    lambda test: os.path.join(current_dir, "Unified", test),
                    skipped_tests,
                )
            )

        def should_keep_test(test):
            return (
                suffix not in test
                if skipped_tests == "All"
                else test not in skipped_tests
            )

        extracted_tests = list(filter(should_keep_test, extracted_tests))
    return extracted_tests


def get_skipped_tests(live_site) -> list[str] | str:
    """
    Read the mapping for the given region and site and return any tests that are marked as skipped.

    Arg:
        live_site (str): The site is being tested.
    Returns:
        list[str] | str: A list of tests that should be skipped, or "All" if all tests should be skipped.
    """
    with open(current_dir + "/constants/" + live_site + ".json", "r") as fp:
        live_site_data = load(fp)
        if live_site_data.get("skip"):
            return "All"
        return live_site_data.get("skipped", [])


def get_flags_and_sanitize(flags_arguments: list[str]) -> list[str]:
    """
    Extract and validate pytest flags from command-line arguments.

    Args:
        flags_arguments (list[str]): List of command-line arguments passed to the script.

    Returns:
        list[str]: A sanitized list of valid pytest flags.

    Raises:
        IndexError: If a flag that is supposed to have an option doesn't
        ValueError: If an arg or flag is not valid.
    """
    # add workers and rerun flaky failed tests.
    flg = []
    expanded_args = [
        flag.split() if "--" not in flag else [flag] for flag in flags_arguments
    ]
    flags_arguments[:] = sum(expanded_args, [])
    for arg in flags_arguments[:]:
        if arg.split("=")[0] in valid_flags:
            if arg in flag_with_parameter:
                try:
                    i = flags_arguments.index(arg)
                    val = int(flags_arguments[i + 1])
                    flg.extend((arg, str(val)))
                    del flags_arguments[i : i + 2]
                except IndexError:
                    logging.warning(f"Argument {arg} doesn't have proper value.")
                    raise IndexError(f"Argument {arg} doesn't have proper value.")
                except ValueError:
                    logging.warning(f"Value for Argument {arg} must be an int.")
                    raise IndexError(f"Value for Argument {arg} must be an int.")
            else:
                flags_arguments.remove(arg)
                flg.append(arg)
        elif arg in valid_region or arg.isdigit():
            continue
        elif arg in valid_sites:
            live_sites.append(arg)
            flags_arguments.remove(arg)
        else:
            logging.warning(f"Invalid Argument: {arg}.")
            raise ValueError(f"Invalid Argument: {arg}.")
    return flg


def run_unified(regions, unified_flags):
    """
    Execute unified tests for multiple regions.

    Args:
        regions (list[str]): A set of region identifiers.
        unified_flags (list[str]): A list of pytest flags to be used.
    """
    unified_tests = get_region_tests("Unified")
    logging.info(f"Testing {live_sites} Sites.")
    for live_site in live_sites:
        # If the live_site is 'demo', skip starting the server
        if live_site == "demo":
            for unified_region in regions:
                run_tests(unified_region, live_site, unified_flags, unified_tests)
        else:
            for unified_region in regions:
                unified_json_path = os.path.join(
                    current_dir, "constants", live_site, unified_region
                )
                if os.path.exists(unified_json_path):
                    with running_server(live_site, unified_region):
                        run_tests(
                            unified_region, live_site, unified_flags, unified_tests
                        )
                else:
                    logging.info(
                        f"No mapping json file for {unified_region} region and {live_site} site."
                    )


if __name__ == "__main__":
    arguments = sys.argv[1:]
    flags = get_flags_and_sanitize(arguments)
    if len(live_sites) == 0:
        # Run on all live sites.
        live_sites = valid_sites
        logging.info(f"Running Against all available live sites ({live_sites}).")
    if len(arguments) == 0:
        ## Run on all Regions.
        logging.info(f"Running Unified Tests for {valid_region} Regions.")
        run_unified(list(valid_region), flags)
    else:
        # run on a given region and sites.
        logging.info(f"Running Unified Tests for {arguments} Regions.")
        run_unified(arguments, flags)
    for site in live_sites:
        # for a given site, run all region-specific tests.
        for region in arguments:
            tests = get_region_tests(region)
            # Check if a field-mapping JSON file is present, pass a test region if it isn't
            json_path = os.path.join(current_dir, "constants", site, region)
            logging.info(f"Running Specific Tests for {region}.")
            # If the live_site is 'demo', skip starting the server
            if site == "demo":
                run_tests(region, site, flags, tests)
            elif os.path.exists(json_path):
                with running_server(site, region):
                    run_tests(region, site, flags, tests)
