import logging
import os
import platform
from typing import List, Tuple

import pytest
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


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


@pytest.fixture()
def opt_headless(request):
    return request.config.getoption("--run-headless")


@pytest.fixture()
def opt_implicit_timeout(request):
    return request.config.getoption("--implicit-timeout")


@pytest.fixture()
def ci(request):
    return request.config.getoption("--ci")

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
    env_prep,
):
    """
    Return the webdriver object.

    All arguments are fixtures being requested.
    """
    options = Options()
    if opt_headless:
        options.add_argument("--headless")
    options.binary_location = fx_executable
    for opt, value in set_prefs:
        options.set_preference(opt, value)
    driver = webdriver.Firefox(options=options)
    driver.implicitly_wait(opt_implicit_timeout)
    yield driver

    driver.quit()


@pytest.fixture()
def screenshot(driver: webdriver.Firefox, ci: bool):
    def _screenshot(filename):
        if not filename.endswith(".png"):
            filename = filename + ".png"
        artifacts_loc = ""
        if ci:
            artifacts_loc = os.path.join("/builds", "worker", "artifacts")
        driver.save_screenshot(os.path.join(artifacts_loc, filename))

    return _screenshot


@pytest.fixture(scope="session", autouse=True)
def faker_seed():
    return 19980331
