import logging
import os

import pytest
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

ABOUT_FIREFOX = "chrome://browser/content/aboutDialog.xhtml"
LATEST_GECKO = "https://github.com/mozilla/geckodriver/releases/latest"


@pytest.fixture()
def add_to_prefs_list(opt_ci):
    # CI runs should be handled by prefs set elsewhere, local runs
    # Should have updates enabled to check update server
    return [] if opt_ci else [("app.update.disabledForTesting", False)]


def _fx_up_to_date(driver: Firefox):
    driver.get(ABOUT_FIREFOX)
    try:
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "noUpdatesFound"))
        )
    except TimeoutException:
        if (
            driver.find_element(By.ID, "otherInstanceHandlingUpdates").is_displayed()
            or driver.find_element(By.ID, "policyDisabled").is_displayed()
        ):
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


def test_fx_version(driver, opt_ci, fx_executable, build_version):
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


def test_gecko_version(driver):
    """Get the geckodriver version"""

    driver.get(LATEST_GECKO)
    WebDriverWait(driver, 20).until(EC.url_contains("tag"))
    url = driver.current_url
    version = url[(url.find("/v") + 2) :]
    assert version == driver.capabilities.get("moz:geckodriverVersion"), (
        f"Geckodriver not updated, should be {version}"
    )
