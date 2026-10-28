import logging

import pytest
from auto_fxui.browser_object import FindToolbar
from auto_fxui.util import BrowserActions
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


@pytest.fixture()
def find_toolbar(driver: Firefox):
    find_toolbar = FindToolbar(driver)
    yield find_toolbar


@pytest.fixture()
def browser_actions(driver: Firefox):
    ba = BrowserActions(driver)
    yield ba


@pytest.fixture()
def timeout():
    return 30


@pytest.fixture()
def prefs_list(add_to_prefs_list: dict):
    """List of prefs to send to main conftest.py driver fixture"""
    prefs = []
    prefs.extend(add_to_prefs_list)
    return prefs


@pytest.fixture()
def add_to_prefs_list():
    return []


@pytest.fixture(autouse=True)
def driver(tmp_path, prefs_list, timeout):
    """
    Return the webdriver object.

    """
    options = Options()
    service_args = ["--allow-system-access"]
    # options.log.level = "trace"
    options.add_argument("--headless")
    options.set_preference("app.update.disabledForTesting", False)

    for opt, value in prefs_list:
        options.set_preference(opt, value)
    try:
        service = Service(service_args=service_args)
        driver = Firefox(service=service, options=options)

        driver.implicitly_wait(timeout)
        WebDriverWait(driver, timeout=40).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        yield driver

    except (WebDriverException, TimeoutException) as e:
        logging.warning(f"DRIVER exception: {e}")
        raise

    finally:
        if "driver" in locals() and driver:
            driver.quit()
