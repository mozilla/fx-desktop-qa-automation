import logging
import os

from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

ABOUT_FIREFOX = "chrome://browser/content/aboutDialog.xhtml"


def _fx_up_to_date(driver: Firefox):
    driver.get(ABOUT_FIREFOX)
    try:
        WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.ID, "noUpdatesFound"))
        )
    except TimeoutException:
        if driver.find_element(By.ID, "otherInstanceHandlingUpdates").is_displayed():
            logging.warning(
                "Could not confirm that Firefox is up to date. Please check manually."
            )
        else:
            raise ValueError("Firefox is not the current version.")


def _get_version(driver: Firefox):
    driver.get(ABOUT_FIREFOX)
    version_el = driver.find_element(By.ID, "version")
    version = version_el.text
    driver.get("about:blank")
    return version


def test_version(driver, opt_ci, fx_executable, build_version):
    """Get the Fx version"""

    displayed_version = _get_version(driver).split(" ")[0]
    if opt_ci:
        if displayed_version not in build_version and not os.environ.get("MANUAL"):
            # Manual flows may test older versions, automatic flows should not
            raise ValueError(
                f"Mismatch between displayed version {displayed_version}"
                f" and actual version {build_version}"
            )
    else:
        _fx_up_to_date(driver)
    driver.quit()
