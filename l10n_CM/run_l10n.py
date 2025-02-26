import logging
import os
import subprocess
import sys
from json import load

current_dir = os.path.dirname(__file__)
valid_flags = {"--run-headless", "-n", "--reruns", "-isolated"}
flag_with_parameter = {"-n", "--reruns"}
valid_region = {"US", "CA", "DE", "FR"}


def run_tests(reg, flg, all_tests):
    """
    Execute the test suite for a given region with specified flags.

    Args:
        reg (str): The test region identifier.
        flg (list[str]): The list of pytest flags to be used.
        all_tests (list[str]): The list of test file paths to execute.
    """
    try:
        if len(all_tests) > 0:
            logging.info(f"Tests for {reg}.")
            os.environ["FX_REGION"] = reg
            subprocess.run(["pytest", *flg, *all_tests], check=True, text=True)
        else:
            logging.info(f"{reg} has no tests.")
    except subprocess.CalledProcessError as e:
        logging.warning(f"Test run failed. {e}")


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
    for arg in flags_arguments[:]:
        if arg in valid_flags:
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
    for unified_region in regions:
        run_tests(unified_region, unified_flags, unified_tests)


if __name__ == "__main__":
    arguments = sys.argv[1:]
    flags = get_flags_and_sanitize(arguments)
    if "-isolated" in flags:
        tests = get_region_tests("Isolated")
        flags.remove("-isolated")
        logging.info(f"Running Region Independent Tests.")
        run_tests("US", flags, tests)
    if len(arguments) == 0:
        logging.info(f"Running Unified Tests for {valid_region} Regions.")
        run_unified(list(valid_region), flags)
    else:
        logging.info(f"Running Unified Tests for {arguments} Regions.")
        run_unified(arguments, flags)
    for region in arguments:
        tests = get_region_tests(region)
        logging.info(f"Running Specific Tests for {region}.")
        run_tests(region, flags, tests)
