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


def test_http_site(
    driver: Firefox, prefs: AboutPrefs, nav: Navigation, panel_ui: PanelUi
):
    """C2300294 Check that HTTP is allowed when appropriate"""

    # Basic functionality
    prefs.open()
    prefs.select_https_only_setting(prefs.HTTPS_ONLY_STATUS.HTTPS_ONLY_DISABLED)
    panel_ui.open_and_switch_to_new_window("tab")

    driver.get(HTTP_SITE)
    nav.element_attribute_contains("lock-icon", "tooltiptext", CONNECTION_NOT_SECURE)

    # Blocking
    driver.switch_to.window(driver.window_handles[0])
    prefs.select_https_only_setting(prefs.HTTPS_ONLY_STATUS.HTTPS_ONLY_ALL)
    driver.switch_to.window(driver.window_handles[1])
    with pytest.raises(WebDriverException):
        driver.refresh()

    # Unblocking - non-private only
    driver.switch_to.window(driver.window_handles[0])
    prefs.select_https_only_setting(prefs.HTTPS_ONLY_STATUS.HTTPS_ONLY_PRIVATE)
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
