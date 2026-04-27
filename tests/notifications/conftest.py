import pytest
from selenium.webdriver import Firefox

from modules.page_object_generics import GenericPage


@pytest.fixture()
def suite_id():
    return ("1907", "Notifications, Push Notifications and Alerts")


@pytest.fixture()
def prefs_list(add_to_prefs_list: dict):
    """List of prefs to send to main conftest.py driver fixture"""
    prefs = []
    prefs.extend(add_to_prefs_list)
    return prefs


@pytest.fixture()
def add_to_prefs_list():
    return []


@pytest.fixture
def web_page(driver: Firefox, temp_selectors):
    def _create(url: str):
        page = GenericPage(driver, url=url).open()
        page.elements |= temp_selectors
        return page

    return _create
