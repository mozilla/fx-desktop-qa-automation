import pytest
from auto_fxui.page_object import GenericPage
from selenium.webdriver import Firefox


@pytest.fixture()
def add_to_prefs_list():
    # 3 is "Open previous windows and tabs", so the page comes back.
    return [("browser.startup.page", 3)]


def test_restart_keeps_driver_and_session(driver: Firefox):
    page = GenericPage(driver, url="about:robots").open()
    old_session = driver.session_id

    page.restart()

    assert page.driver is driver
    assert driver.session_id != old_session
    assert "Gort" in driver.title


def test_restart_twice(driver: Firefox):
    page = GenericPage(driver, url="about:robots").open()

    page.restart()
    page.restart()

    assert "Gort" in driver.title
