import pytest
from auto_fxui.restart import restart_firefox
from selenium.webdriver import Firefox


@pytest.fixture()
def add_to_prefs_list():
    # 3 is "Open previous windows and tabs", so the page comes back.
    return [("browser.startup.page", 3)]


def test_restart_firefox_keeps_driver_and_session(driver: Firefox):
    driver.get("about:robots")
    old_session = driver.session_id

    restarted = restart_firefox(driver)

    assert restarted is driver
    assert driver.session_id != old_session
    assert "Gort" in driver.title


def test_restart_firefox_twice(driver: Firefox):
    driver.get("about:robots")

    restart_firefox(driver)
    restart_firefox(driver)

    assert "Gort" in driver.title
