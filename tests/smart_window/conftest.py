import logging
import time
from os import environ

import psutil
import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from conftest import _parse_window_size
from modules.browser_object import SmartWindow
from modules.taskcluster import get_tc_secret


@pytest.fixture()
def suite_id():
    return ("S70279", "Smart Window")


@pytest.fixture()
def prefs_list(add_to_prefs_list: dict):
    """
    Smart Window ships disabled by default; every test in this suite needs the
    feature available before the window opens.

    First-run onboarding is marked complete with a model chosen, so a Smart
    Window opens straight to its normal view. Tests of sign-up or onboarding
    override add_to_prefs_list to reset these two prefs.

    With first run complete, Firefox opens the AI sidebar whenever a window
    becomes Smart; openByDefault is turned off so a newly activated Smart
    Window starts with the sidebar closed.
    """
    prefs = [
        ("browser.smartwindow.enabled", True),
        ("browser.smartwindow.firstrun.hasCompleted", True),
        # Choice id "1" (Gemini today). Set before launch, so it can't be
        # picked by name like SmartWindowFirstRun.select_model does.
        ("browser.smartwindow.firstrun.modelChoice", "1"),
        ("browser.smartwindow.sidebar.openByDefault", False),
    ]
    prefs.extend(add_to_prefs_list)
    return prefs


@pytest.fixture()
def add_to_prefs_list():
    return []


@pytest.fixture()
def smart_window(driver):
    """Provide the Smart Window BOM for a window still in the Classic state."""
    return SmartWindow(driver)


@pytest.fixture()
def fxa_env():
    # On Taskcluster, read the secret at the task's own level (PRs: 1, main/cron: 3)
    level = environ.get("MOZ_SCM_LEVEL")
    if level:
        fxa_keys = get_tc_secret("ci_waf_token", level=int(level))
        if fxa_keys and fxa_keys.get("stage"):
            environ["CI_WAF_TOKEN"] = fxa_keys["stage"]
    return "stage"


@pytest.fixture()
def active_smart_window(driver):
    """
    Provide the Smart Window BOM with the window already in the Smart Window
    state, for tests about behaviour *inside* a Smart Window.

    See SmartWindow.activate_smart_window for why this does not go through the
    product's own (FxA-gated) entry points.
    """
    sw = SmartWindow(driver)
    sw.activate_smart_window()
    return sw


def _driver_process_tree(driver) -> list[int]:
    """PIDs behind a driver: its geckodriver, plus every Firefox child."""
    proc = getattr(getattr(driver, "service", None), "process", None)
    if proc is None:
        return []
    try:
        parent = psutil.Process(proc.pid)
        return [child.pid for child in parent.children(recursive=True)] + [proc.pid]
    except psutil.Error:
        return []


def _reap(pids: list[int], timeout: int = 10) -> None:
    """Wait for `pids` to exit, killing any that outlive `timeout`."""
    if not pids:
        return
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if not any(psutil.pid_exists(pid) for pid in pids):
            return
        time.sleep(0.2)
    # Leaving these alive would contaminate the next test, so do not just warn.
    for pid in (p for p in pids if psutil.pid_exists(p)):
        logging.warning(f"restart_browser: killing leftover pid {pid}")
        try:
            psutil.Process(pid).kill()
        except psutil.Error:
            pass


@pytest.fixture()
def restart_browser(
    fx_executable,
    geckodriver,
    prefs_list,
    opt_headless,
    opt_implicit_timeout,
    opt_ci,
    opt_window_size,
    fxa_url,
    persistent_profile_dir,
):
    """
    Return a function that quits Firefox and relaunches it on the same profile.

    Needs `use_persistent_profile` True. The quit matters: Firefox flushes
    session state on the way out, so it must close cleanly rather than be
    killed.

    Quitting also invalidates the driver other fixtures hold, so a restart
    test should override fxa_env to None unless it needs FxA -- the autouse
    fxa_waf_bypass talks to the driver in teardown.
    """
    spawned = []

    def _restart(driver: Firefox) -> Firefox:
        if not persistent_profile_dir:
            raise AssertionError(
                "restart_browser requires a use_persistent_profile fixture "
                "returning True; otherwise the profile is a discarded copy"
            )
        driver.quit()
        # Tell the driver fixture not to quit this one again in teardown.
        driver.closed_by_restart = True

        # Mirror the driver fixture, so the relaunch is the same browser.
        options = Options()
        options.binary_location = fx_executable
        options.add_argument("-profile")
        options.add_argument(str(persistent_profile_dir))
        if opt_headless:
            options.add_argument("--headless")
        if fxa_url:
            options.set_preference("identity.fxaccounts.autoconfig.uri", fxa_url)
        for opt, value in prefs_list:
            options.set_preference(opt, value)

        service_args = ["--allow-system-access"]
        service = (
            Service(executable_path=geckodriver, service_args=service_args)
            if geckodriver
            else Service(service_args=service_args)
        )
        restarted = Firefox(service=service, options=options)
        spawned.append(restarted)

        restarted.set_window_size(*_parse_window_size(opt_window_size))
        restarted.implicitly_wait(30 if opt_ci else opt_implicit_timeout)
        WebDriverWait(restarted, timeout=40).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        return restarted

    yield _restart

    for extra in spawned:
        pids = _driver_process_tree(extra)
        try:
            extra.quit()
        except Exception as exc:  # already gone, or never came up
            logging.info(f"restart_browser cleanup: {exc}")
        _reap(pids)

    # Headed only: the relaunched window overlaps the next test's and the
    # panel-menu tests lose focus (measured 10/12 without, 12/12 with).
    if spawned and not opt_headless:
        time.sleep(1)
