import logging
import os
import subprocess
import sys
from json import load

current_dir = os.path.dirname(__file__)


def get_region_tests(test_region: str) -> list[str]:
    path_to_region = current_dir + "/region/"
    with open(path_to_region + test_region + ".json", "r") as fp:
        region_data = load(fp)
        raw_tests = region_data.get("tests", [])
        return (
            list(map(lambda test: current_dir + "/Unified/" + test, raw_tests))
            if len(raw_tests) > 0
            else raw_tests
        )


if __name__ == "__main__":
    valid_region = {"US", "CA", "DE", "FR"}
    regions = sys.argv[1:] if len(sys.argv[1:]) > 0 else valid_region
    headless = "--run-headless" if sys.argv[-1] == "f" else ""
    for region in regions:
        if region == "f":
            break
        if region not in valid_region:
            raise ValueError("Invalid Region.")
        tests = get_region_tests(region)
        try:
            os.environ["STARFOX_REGION"] = region
            subprocess.run(["pytest", headless, *tests], check=True, text=True)
        except subprocess.CalledProcessError as e:
            print(e)
            logging.warn(f"Test run failed. {e}")
