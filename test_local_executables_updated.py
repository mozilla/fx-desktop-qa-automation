import subprocess
import sys

import pytest
import requests
from selenium.webdriver import Firefox

GD_URL = "https://api.github.com/repos/mozilla/geckodriver/releases/latest"


@pytest.fixture()
def prefs_list():
    prefs = []
    return prefs


@pytest.fixture()
def suite_id():
    return ("-1", "None")


def test_local_executables_updated(driver: Firefox, version):
    """
    Test if the local firefox and geckodriver version are up-to-date.
    """
    # Check firefox version
    latest_fx_ver = subprocess.check_output(
        [sys.executable, "./collect_executables.py", "-n"], text=True
    ).split("-")[0]
    local_fx_ver = version[16:]
    if latest_fx_ver != local_fx_ver:
        print("You are not running the latest firefox version!!!")
        raise RuntimeError(
            f"Latest fx version is {latest_fx_ver} but you are running {local_fx_ver}"
        )

    # Check geckodriver version
    latest_gd_ver = get_latest_geckodriver_version()
    local_gd_ver = driver.capabilities["moz:geckodriverVersion"]
    if latest_gd_ver != local_gd_ver:
        print("You are not running the latest geckodriver version!!!")
        print(f"Latest version is {latest_gd_ver} but you are running {local_gd_ver}")
        raise RuntimeError(
            "Update geckodriver here: https://github.com/mozilla/geckodriver/releases/"
        )


def get_latest_geckodriver_version():
    return requests.get(GD_URL).json()["tag_name"][1:]
