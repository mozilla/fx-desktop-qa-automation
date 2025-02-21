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
    if len(sys.argv[1:]) == 0:
        regions = ["Unified"] + list(valid_region)
    else:
        regions = sys.argv[1:]
    for region in regions:
        if region not in valid_region and region != "Unified":
            raise ValueError("Invalid Region.")
        tests = get_region_tests(region)
        try:
            if len(tests) > 0:
                if region != "Unified":
                    os.environ["STARFOX_REGION"] = region
                subprocess.run(["pytest", *tests], check=True, text=True)
            else:
                logging.info(f"{region} has no tests.")
                print(f"{region} has no tests.")
        except subprocess.CalledProcessError as e:
            logging.warn(f"Test run failed. {e}")
