import pytest
import os
import platform
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


def pytest_addoption(parser):
    # set the location of the fx binary from command line if provided
    parser.addoption(
        "--fx-edition",
        action="store",
        default="Custom",
        help="Firefox edition to test. See README for exact paths to builds",
    )

    parser.addoption(
        "--run-headless",
        action="store",
        default=False,
        help="Run in headless mode: --run-headless=True",
    )


@pytest.fixture()
def opt_headless(request):
    return request.config.getoption("--run-headless")


@pytest.fixture()
def fx_executable(request):
    version = request.config.getoption("--fx-edition")

    # Get the platform this is running on
    sys_platform = platform.system()

    # Path to build location.  Use Custom by installing your incident build to the coinciding path.
    location = ""
    if sys_platform == "Windows":
        if version == "Firefox":
            location = "C:\\Program Files\\Mozilla Firefox\\firefox.exe"
        elif version == "Nightly":
            location = "C:\\Program Files\\Nightly Firefox\\firefox.exe"
        elif version == "Custom":
            location = "C:\\Program Files\\Custom Firefox\\firefox.exe"
    elif sys_platform == "Darwin":
        if version == "Firefox":
            location = "/Applications/Firefox.app/Contents/MacOS/firefox"
        elif version == "Nightly":
            location = "/Applications/Nightly Firefox.app/Contents/MacOS/firefox"
        elif version == "Custom":
            location = "/Applications/Custom Firefox.app/Contents/MacOS/firefox"
    elif sys_platform == "Linux":
        user = os.environ.get("USER")
        if version == "Firefox":
            location = f"/home/{user}/Desktop/Firefox/firefox"
        elif version == "Nightly":
            location = f"/home/{user}/Desktop/Nightly Firefox/firefox"
        elif version == "Custom":
            location = f"/home/{user}/Desktop/Custom Firefox/firefox"

    return location


@pytest.fixture(autouse=True)
def driver(fx_executable, opt_headless, test_opts):
    # create a new instance of the browser
    options = Options()
    if opt_headless:
        options.add_argument("--headless")
    options.binary_location = fx_executable
    for opt, value in test_opts:
        options.set_preference(opt, value)
    s = webdriver.Firefox(options=options)
    yield s

    s.quit()


@pytest.fixture(scope="session", autouse=True)
def faker_seed():
    return 19980331
