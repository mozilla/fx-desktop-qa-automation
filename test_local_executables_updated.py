import pytest
import requests
from selenium.webdriver import Firefox
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

GD_URL = "https://api.github.com/repos/mozilla/geckodriver/releases/latest"


@pytest.fixture()
def prefs_list():
    prefs = [("app.update.disabledForTesting", False)]
    return prefs


@pytest.fixture()
def suite_id():
    return ("-1", "None")


def test_local_executables_updated(driver: Firefox, version):
    """
    Test if the local firefox and geckodriver version are up-to-date.
    """
    # Check firefox version
    driver.get("chrome://browser/content/aboutDialog.xhtml")
    WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located(("id", "noUpdatesFound"))
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
