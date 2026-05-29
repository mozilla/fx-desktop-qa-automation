import pytest
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver import Firefox

from modules.browser_object import Navigation, PanelUi
from modules.page_object import AboutPrefs


@pytest.fixture()
def test_case():
    return "2300294"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("dom.security.https_only_mode_ever_enabled", True),
        ("dom.security.https_only_mode_ever_enabled_pbm", True),
        ("dom.security.https_first", False),
        ("dom.security.https_first_add_exception_on_failure", False),
        ("dom.security.https_first_pbm", False),
        ("dom.security.https_first_schemeless", False),
    ]


HTTP_SITE = "http://http.badssl.com/"
CONNECTION_NOT_SECURE = "Connection is not secure"


def test_http_site(driver: Firefox):
    """C2300294 Check that HTTP is allowed when appropriate"""

    # Instantiate objects
    prefs = AboutPrefs(driver, category="privacy")
    nav = Navigation(driver)
    panel_ui = PanelUi(driver)

    # Basic functionality
    prefs.open()
    prefs.open_connection_advanced()
    prefs.select_https_only_setting("disabled")
    panel_ui.open_and_switch_to_new_window("tab")

    driver.get(HTTP_SITE)
    nav.element_attribute_contains("lock-icon", "tooltiptext", CONNECTION_NOT_SECURE)

    # Blocking
    driver.switch_to.window(driver.window_handles[0])
    prefs.select_https_only_setting("all")
    driver.switch_to.window(driver.window_handles[1])
    with pytest.raises(WebDriverException):
        driver.refresh()

    # Unblocking - non-private only
    driver.switch_to.window(driver.window_handles[0])
    prefs.select_https_only_setting("private")
    driver.switch_to.window(driver.window_handles[1])

    driver.refresh()
    nav.element_attribute_contains("lock-icon", "tooltiptext", CONNECTION_NOT_SECURE)

    # Private browsing - blocked
    panel_ui.open_and_switch_to_new_window("private")

    with pytest.raises(WebDriverException):
        driver.get(HTTP_SITE)
    try:
        driver.get(HTTP_SITE)
        assert "badssl" not in driver.current_url, "Site should not be displayed"
    except (TimeoutException, WebDriverException):
        pass
