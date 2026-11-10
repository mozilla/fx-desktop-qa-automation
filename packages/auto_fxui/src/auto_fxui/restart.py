"""Restart Firefox mid-test on the same profile, keeping the same driver object."""

import logging
import os
import socket
import subprocess
import time
from pathlib import Path

from selenium.common.exceptions import WebDriverException
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service

# Marionette writes its port here at startup and removes it on shutdown.
ACTIVE_PORT_FILE = "MarionetteActivePort"
# geckodriver's --allow-system-access gives the Firefox it starts this variable.
SYSTEM_ACCESS_ENV = "MOZ_REMOTE_ALLOW_SYSTEM_ACCESS"
SYSTEM_ACCESS_ARG = "--allow-system-access"

_BROWSER_INFO_JS = """
return {
  exe: Services.dirsvc.get("XREExeF", Ci.nsIFile).path,
  profile: Services.dirsvc.get("ProfD", Ci.nsIFile).path,
  headless: Cc["@mozilla.org/gfx/info;1"].getService(Ci.nsIGfxInfo).isHeadless,
};
"""


class _Services:
    """What WebDriver.quit() stops after a restart, in an order that frees the profile."""

    def __init__(self, attached: Service, firefox: subprocess.Popen, original: Service):
        self.attached = attached
        self.firefox = firefox
        self.original = original

    def stop(self):
        _stop_service(self.attached)
        # geckodriver leaves a Firefox it attached to running when the session ends.
        _end_process(self.firefox)
        # Last: the original geckodriver deletes the profile when it stops.
        _stop_service(self.original)


def _end_process(process: subprocess.Popen) -> None:
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()


def _stop_service(service: Service) -> None:
    try:
        service.stop()
    except Exception as error:  # one failing shouldn't leave the rest running
        logging.warning("restart_firefox: stopping %s: %s", service, error)


def restart_firefox(
    driver: Firefox, resume_session: bool = False, timeout: float = 60
) -> Firefox:
    """
    Quit Firefox cleanly and start it again on the same profile, reattaching `driver` to it.

    Parameters
    ----------
    driver : Firefox
        The test's driver. Its geckodriver must have been started with
        --allow-system-access, as STARfox's are.
    resume_session : bool
        Restore the session once on the next start, as Firefox's own Restart
        does, whatever browser.startup.page says.
    timeout : float
        Seconds to wait for Firefox to quit, and again for it to come back.

    Returns
    -------
    Firefox
        The same driver object, so fixtures and page objects holding it keep
        working; its quit() at teardown closes the restarted Firefox too.
    """
    with driver.context(driver.CONTEXT_CHROME):
        info = driver.execute_script(_BROWSER_INFO_JS)
        if resume_session:
            driver.execute_script(
                "Services.prefs.setBoolPref('browser.sessionstore.resume_session_once', true);"
            )
    window_size = driver.get_window_size()
    timeouts = driver.timeouts
    profile = Path(info["profile"])
    previous = driver.service
    # On a second restart, the geckodriver that owns the profile is the first one.
    original = previous.original if isinstance(previous, _Services) else previous
    system_access = SYSTEM_ACCESS_ARG in (getattr(original, "service_args", None) or [])

    _quit_in_place(driver)
    _wait_for(
        lambda: not (profile / ACTIVE_PORT_FILE).exists(),
        timeout,
        "Firefox did not quit",
    )
    if isinstance(previous, _Services):
        _stop_service(previous.attached)

    firefox, port = _launch(info, system_access, timeout)
    service_args = ["--connect-existing", "--marionette-port", str(port)]
    if system_access:
        service_args.append(SYSTEM_ACCESS_ARG)
    service = Service(executable_path=original.path, service_args=service_args)
    try:
        attached = Firefox(service=service, options=Options())
    except Exception:
        _stop_service(service)
        _end_process(firefox)
        raise

    # Point the caller's driver at the new session.
    driver.session_id = attached.session_id
    driver.command_executor = attached.command_executor
    driver.caps = attached.caps
    driver.service = _Services(service, firefox, original)
    driver.timeouts = timeouts
    driver.set_window_size(window_size["width"], window_size["height"])
    return driver


def _quit_in_place(driver: Firefox) -> None:
    """Ask Firefox to quit, so it saves the session; driver.quit() would delete the profile."""
    # Not driver.context(): leaving that block talks to the session that just closed.
    driver.set_context(driver.CONTEXT_CHROME)
    try:
        driver.execute_script("Services.startup.quit(Ci.nsIAppStartup.eAttemptQuit);")
    except WebDriverException as error:  # the connection can drop mid-reply
        logging.info("restart_firefox: quit: %s", error)


def _launch(
    info: dict, system_access: bool, timeout: float
) -> tuple[subprocess.Popen, int]:
    """Start Firefox on the profile with Marionette on; return it and its Marionette port."""
    args = [info["exe"], "--marionette", "-foreground", "-no-remote"]
    args += ["-profile", info["profile"]]
    if info["headless"]:
        args.append("--headless")
    env = dict(os.environ)
    if system_access:
        env[SYSTEM_ACCESS_ENV] = "1"
    port_file = Path(info["profile"]) / ACTIVE_PORT_FILE

    # A second try covers the old Firefox still holding the profile lock for a
    # moment after its port file went: the new one then exits straight away.
    for attempt in range(2):
        process = subprocess.Popen(
            args, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline and process.poll() is None:
            port = _read_port(port_file)
            if port and _port_open(port):
                return process, port
            time.sleep(0.25)
        if process.poll() is None:
            process.kill()
            break
        logging.info("restart_firefox: Firefox exited at start (try %d)", attempt + 1)
        time.sleep(2)
    raise AssertionError(f"Firefox did not restart on {info['profile']}")


def _read_port(port_file: Path) -> int | None:
    try:
        return int(port_file.read_text().strip())
    except (OSError, ValueError):
        return None


def _port_open(port: int) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=1):
            return True
    except OSError:
        return False


def _wait_for(condition, timeout: float, message: str) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if condition():
            return
        time.sleep(0.2)
    raise AssertionError(message)
