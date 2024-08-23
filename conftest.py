import datetime
import logging
import os
import platform
import re
from shutil import unpack_archive
from typing import Callable, List, Tuple, Union

import pytest
from PIL import Image, ImageGrab
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def screenshot_content(driver: Firefox, opt_ci: bool, test_name: str) -> None:
    """
    Screenshots the current browser, saves with appropriate test name and date for reference
    """
    current_time = str(datetime.datetime.now())
    current_time = re.sub(r"[^\w_. -]", "_", current_time)
    filename = f"{test_name}_{current_time}_image"
    try:
        _screenshot_whole_screen(f"{filename}_screen", driver, opt_ci)
    except Exception as e:
        logging.error(f"Unable to screenshot entire screen {e}")

    try:
        _screenshot(filename, driver, opt_ci)
    except Exception as e:
        logging.error(f"Unable to screenshot driver window {e}")


def log_content(opt_ci: bool, driver: Firefox, test_name: str) -> None:
    """
    Logs the current browser content, with the appropriate test name and date for reference.
    """
    artifacts_loc = "artifacts" if opt_ci else ""
    current_time = str(datetime.datetime.now())
    current_time = re.sub(r"[^\w_. -]", "_", current_time)
    fullpath_content = os.path.join(
        artifacts_loc, f"{test_name}_{current_time}_content.txt"
    )
    fullpath_chrome = os.path.join(
        artifacts_loc, f"{test_name}_{current_time}_chrome.txt"
    )

    try:
        # Save Chrome context page source
        with open(fullpath_chrome, "w", encoding="utf-8") as fh:
            with driver.context(driver.CONTEXT_CHROME):
                output_contents = driver.page_source
                fh.write(output_contents)

        # Save Content context page source
        with open(fullpath_content, "w", encoding="utf-8") as fh:
            output_contents = driver.page_source
            fh.write(output_contents)
    except Exception as e:
        logging.error(f"Could not log the html content because of {e}")
    return


def sanitize_filename(filename):
    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', "", filename)
    # Limit to 200 characters
    return sanitized[:200]


def pytest_exception_interact(node, call, report):
    """
    Method that wraps all test execution, on any exception/failure an artifact with the information about the failure is kept.
    """
    if report.failed:
        try:
            test_name = node.name
            test_name = sanitize_filename(test_name)
            logging.info(f"Handling exception for test: {test_name}")
            if hasattr(node, "funcargs"):
                logging.info(
                    f"NODE LOGS HERE {node.funcargs}\n THE FAILED TEST: {test_name}"
                )
                driver = node.funcargs.get("driver")
                opt_ci = node.funcargs.get("opt_ci")
                if driver and opt_ci:
                    logging.info("Writing artifacts...")
                    log_content(opt_ci, driver, test_name)
                    screenshot_content(driver, opt_ci, test_name)
            else:
                logging.error("Error occurred during collection.")
        except Exception:
            logging.error("Something went wrong with the exception catching.")


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


def _screenshot(filename: str, driver: Firefox, opt_ci: bool):
    if not filename.endswith(".png"):
        filename = filename + ".png"
    artifacts_loc = ""
    if opt_ci:
        artifacts_loc = "artifacts"
    fullpath = os.path.join(artifacts_loc, filename)
    driver.save_screenshot(fullpath)
    return fullpath


def _screenshot_whole_screen(filename: str, driver: Firefox, opt_ci: bool):
    if not filename.endswith(".png"):
        filename = filename + ".png"
    artifacts_loc = ""
    if opt_ci:
        artifacts_loc = "artifacts"
    fullpath = os.path.join(artifacts_loc, filename)
    screenshot = None
    if platform.system() == "Darwin":
        screenshot = ImageGrab.grab()
        screenshot.save(fullpath)

        # compress the image (OSX generates large screenshots)
        image = Image.open(fullpath)
        width, height = image.size
        new_size = (width // 2, height // 2)
        resized_image = image.resize(new_size)
        resized_image.save(fullpath, optimize=True, quality=50)
    elif platform.system() == "Linux":
        return None
    else:
        screenshot = ImageGrab.grab()
        screenshot.save(fullpath)
    return fullpath


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
def downloads_folder(sys_platform):
    """Return the downloads folder location for this OS"""
    if sys_platform == "Windows":
        user = os.environ.get("USERNAME")
        return f"C:\\Users\\{user}\\Downloads"
    elif sys_platform == "Darwin":  # MacOS
        user = os.environ.get("USER")
        return f"/Users/{user}/Downloads"
    elif sys_platform == "Linux":
        user = os.environ.get("USER")
        return f"/home/{user}/Downloads"


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


@pytest.fixture()
def use_profile():
    """
    Return or yield <string> in a fixture of this name in a test
    to use ./profiles/<string> as the profile for a given test
    """
    yield False


@pytest.fixture(autouse=True)
def driver(
    fx_executable: str,
    opt_headless: bool,
    opt_implicit_timeout: int,
    set_prefs: List[Tuple],
    opt_ci: bool,
    opt_window_size: str,
    use_profile: Union[bool, str],
    env_prep,
    tmp_path,
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

    use_profile: Union[bool, str]
        Location inside ./profiles to find the profile to use, False if no profile needed.

    env_prep: None
        Fixture that does other environment work, like set logging levels.
    """
    try:
        options = Options()
        if opt_headless:
            options.add_argument("--headless")
        options.binary_location = fx_executable
        if use_profile:
            profile_path = tmp_path / use_profile
            unpack_archive(os.path.join("profiles", f"{use_profile}.zip"), profile_path)
            options.profile = profile_path
        for opt, value in set_prefs:
            options.set_preference(opt, value)
        driver = Firefox(options=options)
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
        WebDriverWait(driver, timeout=40).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        yield driver
    except (WebDriverException, TimeoutException) as e:
        logging.warning(f"DRIVER exception: {e}")
    finally:
        if "driver" in locals() or "driver" in globals():
            driver.quit()


@pytest.fixture()
def screenshot(driver: Firefox, opt_ci: bool) -> Callable:
    """
    Factory fixture that returns a screenshot function.
    """

    def screenshot_wrapper(filename: str) -> str:
        return _screenshot(filename, driver, opt_ci)

    return screenshot_wrapper


@pytest.fixture()
def delete_files_regex_string():
    """
    Tell the delete_files fixture re.match() what files to delete.
    In ./conftest.py, use a regex that is unlikely to match things.
    """
    return r"zzxqxzqx"


@pytest.fixture()
def delete_files(sys_platform, delete_files_regex_string):
    """Remove the files after the test finishes, should work for Mac/Linux/MinGW"""

    def _delete_files():
        if sys_platform.startswith("Win"):
            if os.environ.get("GITHUB_ACTIONS") == "true":
                downloads_folder = os.path.join(
                    "C:", "Users", "runneradmin", "Downloads"
                )
            else:
                home_folder = os.path.join(
                    os.environ.get("HOMEDRIVE"), os.environ.get("HOMEPATH")
                )
                downloads_folder = os.path.join(home_folder, "Downloads")
        else:
            home_folder = os.environ.get("HOME")
            downloads_folder = os.path.join(home_folder, "Downloads")
            logging.info(os.path.exists(downloads_folder))

        for file in os.listdir(downloads_folder):
            delete_files_regex = re.compile(delete_files_regex_string)
            if delete_files_regex.match(file):
                os.remove(os.path.join(downloads_folder, file))

    _delete_files()
    yield True
    _delete_files()


@pytest.fixture()
def version(driver: Firefox):
    return driver.capabilities["browserVersion"]


@pytest.fixture(scope="session", autouse=True)
def faker_seed():
    return 19980331


@pytest.fixture()
def is_gha():
    return os.environ.get("GITHUB_ACTIONS") == "true"


@pytest.fixture(scope="session")
def fillable_pdf_url():
    return "https://www.uscis.gov/sites/default/files/document/forms/i-9.pdf"
