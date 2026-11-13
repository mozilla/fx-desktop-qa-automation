import pytest
from auto_fxui.browser_object import Devtools, Navigation, PanelUi
from selenium.webdriver import Firefox

SCHEMELESS_URL = "example.com"
HTTP_URL = "http://example.com"
HTTPS_URL = "https://example.com"
UPGRADE_MESSAGE = (
    "HTTPS-First Mode: Upgrading insecure request “http://example.com/” to use “https”."
)
EXCEPTION_MESSAGE = (
    "HTTPS-First Mode: Adding exception to temporarily prevent further attempts "
    "to automatically load “http://example.com” securely."
)


@pytest.fixture()
def test_case():
    return "1362264"


@pytest.fixture()
def add_to_prefs_list():
    return [
        ("dom.security.https_first_pbm", True),
        ("dom.security.https_first_schemeless", False),
    ]


def test_https_first_mode_message_display(driver: Firefox):
    """
    C1362264 - Check that HTTPS First Mode messages are properly displayed in the browser console
    """
    # Instantiate objects
    panel = PanelUi(driver)
    nav = Navigation(driver)
    devtools = Devtools(driver)

    # check URL is upgraded to HTTPS and console contains upgrade message for schemeless URL
    panel.open_and_switch_to_new_window("private")
    nav.search(SCHEMELESS_URL)
    panel.url_contains("https://")
    devtools.expect_console_contains(UPGRADE_MESSAGE)

    # check URL is not upgraded to HTTPS and console contains exception message for HTTP URL
    panel.open_and_switch_to_new_window("tab")
    nav.search(HTTP_URL)
    panel.url_contains("http://")
    devtools.expect_console_contains(EXCEPTION_MESSAGE)

    # close previous private tabs and clear the console
    for handle in driver.window_handles[1:]:
        driver.switch_to.window(handle)
        driver.close()
    driver.switch_to.window(driver.window_handles[0])
    devtools.clear_console()

    # check no HTTPS-First mode logs displayed for HTTPS URL
    panel.open_and_switch_to_new_window("private")
    nav = Navigation(driver)  # The old one caches the closed window's address bar
    nav.search(HTTPS_URL)
    panel.url_contains("https://")
    panel.title_contains("Example Domain")
    assert not devtools.console_contains("HTTPS-First Mode")
