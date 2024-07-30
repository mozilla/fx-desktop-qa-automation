import datetime
import logging
import os
import platform
import re
import sys
from typing import Callable, List, Tuple

import pytest
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options

# pipenv run pytest --fx-executable ./firefox/firefox -n 4 .


def screenshot_content(driver: Firefox, opt_ci: bool, test_name: str) -> None:
    """
    Screenshots the current browser, saves with appropriate test name and date for reference
    """
    artifacts_loc = "artifacts" if opt_ci else ""
    current_time = str(datetime.datetime.now())
    current_time = re.sub(r"[^\w_. -]", "_", current_time)
    filename = f"{test_name}_{current_time}_image"
    if not filename.endswith(".png"):
        filename = filename + ".png"
        artifacts_loc = ""
        if opt_ci:
            artifacts_loc = "artifacts"
        fullpath = os.path.join(artifacts_loc, filename)
        driver.save_screenshot(fullpath)
    return


def log_content(opt_ci: bool, driver: Firefox, test_name: str) -> None:
    """
    Logs the current browser content, with the appropriate test name and date for reference.
    """
    artifacts_loc = "artifacts" if opt_ci else ""
    current_time = str(datetime.datetime.now())
    current_time = re.sub(r"[^\w_. -]", "_", current_time)
    fullpath_chrome = os.path.join(
        artifacts_loc, f"{test_name}_{current_time}_content.txt"
    )
    fullpath_content = os.path.join(
        artifacts_loc, f"{test_name}_{current_time}_chrome.txt"
    )

    # Save Chrome context page source
    with open(fullpath_chrome, "w") as fh:
        with driver.context(driver.CONTEXT_CHROME):
            output_contents = driver.page_source
            fh.write(output_contents)

    # Save Content context page source
    with open(fullpath_content, "w") as fh:
        output_contents = driver.page_source
        fh.write(output_contents)
    return


def pytest_exception_interact(node, call, report):
    """
    Method that wraps all test execution, on any exception/failure an artifact with the information about the failure is kept.
    """
    if report.failed:
        try:
            test_name = node.name
            logging.info(f"Handling exception for test: {test_name}")
            print(
                f"NODE LOGS HERE {node.funcargs}\n THE FAILED TEST: {test_name}",
                file=sys.stderr,
            )
            driver = node.funcargs.get("driver")
            opt_ci = node.funcargs.get("opt_ci")
            if driver:
                log_content(opt_ci, driver, test_name)
                screenshot_content(driver, opt_ci, test_name)
        except Exception as e:
            logging.warning("Something went wrong with the exception catching.")
            raise e


def pytest_addoption(parser):
    """Set custom command-line options"""
    parser.addoption(
        "--ci",
        action="store_true",
        default=False,
        help="Is this running in a CI environment?",
    )

    parser.addoption(
        "--fx-channel",
        action="store",
        default="Custom",
        help="Firefox channel to test. See README for exact paths to builds",
    )

    parser.addoption(
        "--fx-executable",
        action="store",
        default="",
        help="Path to Fx executable. Will overwrite --fx-channel.",
    )

    parser.addoption(
        "--run-headless",
        action="store_true",
        default=False,
        help="Run in headless mode: --run-headless",
    )

    parser.addoption(
        "--implicit-timeout",
        action="store",
        default=10,
        help="Timeout for implicit waits, set 0 for no wait (default 10)",
    )

    parser.addoption(
        "--window-size",
        action="store",
        default="1152x864",
        help="Size for Fx window, default is '1152x864'",
    )


@pytest.fixture()
def opt_headless(request):
    return request.config.getoption("--run-headless")


@pytest.fixture()
def opt_implicit_timeout(request):
    return request.config.getoption("--implicit-timeout")


@pytest.fixture()
def opt_ci(request):
    return request.config.getoption("--ci")


@pytest.fixture()
def opt_window_size(request):
    return request.config.getoption("--window-size")


@pytest.fixture()
def sys_platform():
    return platform.system()


@pytest.fixture()
def fx_executable(request, sys_platform):
    """Get the Fx executable path based on platform and edition request."""
    version = request.config.getoption("--fx-channel")
    location = request.config.getoption("--fx-executable")
    if location:
        return location

    # Path to build location.  Use Custom by installing your incident build to the coinciding path.
    location = ""
    if sys_platform == "Windows":
        if version == "Firefox":
            location = "C:\\Program Files\\Mozilla Firefox\\firefox.exe"
        elif version == "Nightly":
            location = "C:\\Program Files\\Firefox Nightly\\firefox.exe"
        elif version == "Custom":
            location = "C:\\Program Files\\Custom Firefox\\firefox.exe"
    elif sys_platform == "Darwin":
        if version == "Firefox":
            location = "/Applications/Firefox.app/Contents/MacOS/firefox"
        elif version == "Nightly":
            location = "/Applications/Firefox Nightly.app/Contents/MacOS/firefox"
        elif version == "Custom":
            location = "/Applications/Custom Firefox.app/Contents/MacOS/firefox"
    elif sys_platform == "Linux":
        user = os.environ.get("USER")
        if version == "Firefox":
            location = f"/home/{user}/Desktop/Firefox/firefox"
        elif version == "Nightly":
            location = f"/home/{user}/Desktop/Firefox Nightly/firefox"
        elif version == "Custom":
            location = f"/home/{user}/Desktop/Custom Firefox/firefox"

    return location


@pytest.fixture(autouse=True)
def env_prep():
    logging.getLogger("werkzeug").setLevel(logging.WARNING)


@pytest.fixture(autouse=True)
def driver(
    fx_executable: str,
    opt_headless: bool,
    opt_implicit_timeout: int,
    set_prefs: List[Tuple],
    opt_ci: bool,
    opt_window_size: str,
    env_prep,
):
    """
    Return the webdriver object.

    All arguments are fixtures being requested, rather than parameters.

    Fixtures
    --------

    fx_executable: str
        Location of the Firefox executable.

    opt_headless: bool
        Whether pytest was run with --run-headless.

    opt_implicit_timeout: int
        Timeout, in seconds for driver-level wait attribute.

    set_prefs: List[Tuple]
        Preferences to set before the Firefox object is created.
        Usually set in the conftest.py inside a test suite folder.

    opt_ci: bool
        Whether pytest was run with --ci.

    opt_window_size: str
        String describing the window size for the Firefox window.

    env_prep: None
        Fixture that does other environment work, like set logging levels.
    """
    try:
        options = Options()
        if opt_headless or opt_ci:
            options.add_argument("--headless")
        options.binary_location = fx_executable
        for opt, value in set_prefs:
            options.set_preference(opt, value)
        driver = webdriver.Firefox(options=options)
        separator = "x"
        if separator not in opt_window_size:
            if "by" in opt_window_size:
                separator = "by"
            elif "," in opt_window_size:
                separator = ","
            elif " " in opt_window_size:
                separator = " "
        winsize = [int(s) for s in opt_window_size.split(separator)]
        driver.set_window_size(*winsize)
        timeout = 30 if opt_ci else opt_implicit_timeout
        driver.implicitly_wait(timeout)
        yield driver
    except WebDriverException as e:
        logging.warning(f"DRIVER exception: {e}")
    finally:
        if "driver" in locals() or "driver" in globals():
            driver.quit()


@pytest.fixture()
def screenshot(driver: webdriver.Firefox, opt_ci: bool) -> Callable:
    """
    Factory fixture that returns a screenshot function.
    """

    def _screenshot(filename: str) -> str:
        """
        Given a short filename, save a screenshot and return the image's full path.
        """
        if not filename.endswith(".png"):
            filename = filename + ".png"
        artifacts_loc = ""
        if opt_ci:
            artifacts_loc = "artifacts"
        fullpath = os.path.join(artifacts_loc, filename)
        driver.save_screenshot(fullpath)
        return fullpath

    return _screenshot


@pytest.fixture()
def version(driver: webdriver.Firefox):
    return driver.capabilities["browserVersion"]


@pytest.fixture(scope="session", autouse=True)
def faker_seed():
    return 19980331


@pytest.fixture(scope="session")
def fillable_pdf_url():
    return "https://www.uscis.gov/sites/default/files/document/forms/i-9.pdf"


def log_page_content(driver: webdriver.Firefox, opt_ci: bool):
    """
    Function that saves the html content into the artifacts on a failed test
    """

    def _log_page_content(opt_ci: bool):
        artifacts_loc = "artifacts" if opt_ci else ""
        fullpath_chrome = os.path.join(artifacts_loc, "page_source_chrome.html")
        fullpath_content = os.path.join(artifacts_loc, "page_source_content.html")

        # Save Chrome context page source
        with open(fullpath_chrome, "w") as fh:
            driver.switch_to.context(driver.CONTEXT_CHROME)
            output_contents = driver.page_source.replace("><", ">\n<")
            fh.write(output_contents)

        # Save Content context page source
        with open(fullpath_content, "w") as fh:
            driver.switch_to.context(driver.CONTEXT_CONTENT)
            output_contents = driver.page_source.replace("><", ">\n<")
            fh.write(output_contents)

    return _log_page_content(opt_ci)
