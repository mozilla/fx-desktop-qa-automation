import pytest
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, PanelUi
from modules.page_object import AboutPrefs


@pytest.fixture()
def test_case():
    return "2300294"


@pytest.fixture()
def set_prefs():
    return [
        ("dom.security.https_only_mode_ever_enabled", True),
        ("dom.security.https_only_mode_ever_enabled_pbm", True),
        ("dom.security.https_first", False),
        ("dom.security.https_first_add_exception_on_failiure", False),
        ("dom.security.https_first_pbm", False),
        ("dom.security.https_first_schemeless", False),
    ]


HTTP_SITE = "http://http.badssl.com/"
CONNECTION_NOT_SECURE = "Connection is not secure"


def test_http_site(driver: Firefox):
    """C2300294 Check that HTTP is allowed when appropriate"""

    # Basic functionality
    prefs = AboutPrefs(driver, category="privacy")
    prefs.open()
    prefs.select_https_only_setting(prefs.HTTPS_ONLY_STATUS.HTTPS_ONLY_DISABLED)
    driver.get(HTTP_SITE)
    nav = Navigation(driver)
    nav.element_attribute_contains("lock-icon", "tooltiptext", CONNECTION_NOT_SECURE)

    # Blocking
    prefs.open()
    prefs.select_https_only_setting(prefs.HTTPS_ONLY_STATUS.HTTPS_ONLY_ALL)
    driver.refresh()
    try:
        driver.get(HTTP_SITE)
        assert False, "Site should be blocked"
    except (TimeoutException, WebDriverException):
        pass

    # Unblocking - non-private only
    prefs.open()
    prefs.select_https_only_setting(prefs.HTTPS_ONLY_STATUS.HTTPS_ONLY_PRIVATE)
    driver.refresh()
    driver.get(HTTP_SITE)
    nav.element_attribute_contains("lock-icon", "tooltiptext", CONNECTION_NOT_SECURE)

    # Private browsing - blocked
    hamburger = PanelUi(driver)
    hamburger.open_private_window()
    nav.switch_to_new_window()
    try:
        driver.get(HTTP_SITE)
        assert False, "Site should be blocked"
    except (TimeoutException, WebDriverException):
        pass
