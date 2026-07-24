import logging

import pytest
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from modules.browser_object import Navigation, PanelUi
from modules.page_object import GenericPage

URL = "https://senglehardt.com/test/dfpi/storage_access_api.html"


@pytest.fixture()
def test_case():
    return "2359319"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("browser.privatebrowsing.resetPBM.enabled", True),
        ("browser.privatebrowsing.felt-privacy-v1", True),
    ]


def _log_frame_state(driver: Firefox, expected: str) -> None:
    """DIAGNOSTIC: on timeout, dump every top-level iframe's size/content so CI reveals why frame(0) is blank."""
    try:
        driver.switch_to.default_content()
        frames = driver.find_elements(By.TAG_NAME, "iframe")
        summary = []
        for i in range(len(frames)):
            try:
                driver.switch_to.default_content()
                driver.switch_to.frame(i)
                src = driver.page_source
                summary.append(
                    f"frame[{i}] len={len(src)} "
                    f"has_expected={expected in src} has_cookie_text={'Cookies' in src}"
                )
            except WebDriverException as exc:
                summary.append(f"frame[{i}] error={type(exc).__name__}")
        driver.switch_to.default_content()
        logging.warning(
            "DIAG timed out for %r | url=%s | top_iframes=%d | handles=%s | %s",
            expected,
            driver.current_url,
            len(frames),
            driver.window_handles,
            " || ".join(summary),
        )
    except WebDriverException as exc:
        logging.warning("DIAG dump failed: %s", exc)


def test_end_private_session_clears_cookies(driver: Firefox):
    """
    C2359319 - Verify that via end a private session button cookies are cleared
    """
    # Instantiate objects
    nav = Navigation(driver)
    panel = PanelUi(driver)
    page = GenericPage(driver, url=URL)

    # Open a private window and switch to it
    panel.open_and_switch_to_new_window("private")

    # Open site
    page.open()

    # Refresh the page to make sure the cookie is set and stored
    nav.click_on("refresh-button")
    driver.switch_to.frame(0)
    try:
        nav.custom_wait(timeout=30).until(
            lambda d: "Cookies already set" in d.page_source
        )
    except TimeoutException:
        _log_frame_state(driver, "Cookies already set")
        raise

    # Click on the data clearance (End private session) button
    driver.switch_to.default_content()
    nav.end_private_session()
    driver.switch_to.window(driver.window_handles[-1])

    # Navigate back to the site and verify cookies are cleared
    page.open()
    driver.switch_to.frame(0)
    try:
        nav.custom_wait(timeout=30).until(
            lambda d: "Cookies not yet set" in d.page_source
        )
    except TimeoutException:
        _log_frame_state(driver, "Cookies not yet set")
        raise
