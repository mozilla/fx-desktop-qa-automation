import pytest
from selenium.webdriver import Firefox

from modules.browser_object import Navigation


@pytest.fixture()
def test_case():
    return "2300294"


@pytest.fixture()
def set_prefs():
    return [("dom.security.https_only_mode", False)]


HTTP_SITE = "http://www.http2demo.io/"
CONNECTION_NOT_SECURE = "Connection is not secure"


def test_http_site(driver: Firefox):
    driver.get(HTTP_SITE)
    nav = Navigation(driver)
    nav.element_attribute_contains("lock-icon", "tooltiptext", CONNECTION_NOT_SECURE)
