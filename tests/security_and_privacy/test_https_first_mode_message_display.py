import pytest
from auto_fxui.browser_object import Navigation, PanelUi
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


def get_console_messages(driver: Firefox) -> list[str]:
    """Return every message logged to the browser console."""
    with driver.context(driver.CONTEXT_CHROME):
        return driver.execute_script(
            "return Services.console.getMessageArray().map(m => m.message);"
        )


def console_contains(driver: Firefox, text: str) -> bool:
    return any(text in m for m in get_console_messages(driver))


def test_https_first_mode_message_display(driver: Firefox):
    """
    C1362264 - Check that HTTPS First Mode messages are properly displayed in the browser console
    """
    # Instantiate objects
    panel = PanelUi(driver)
    nav = Navigation(driver)

    # check URL is upgraded to HTTPS and console contains upgrade message for schemeless URL
    panel.open_and_switch_to_new_window("private")
    nav.search(SCHEMELESS_URL)
    panel.url_contains("https://")
    panel.expect(lambda _: console_contains(driver, UPGRADE_MESSAGE))

    # check URL is not upgraded to HTTPS and console contains exception message for HTTP URL
    panel.open_and_switch_to_new_window("tab")
    nav.search(HTTP_URL)
    panel.url_contains("http://")
    panel.expect(lambda _: console_contains(driver, EXCEPTION_MESSAGE))

    # close previous private tabs and clear the console
    for handle in driver.window_handles[1:]:
        driver.switch_to.window(handle)
        driver.close()
    driver.switch_to.window(driver.window_handles[0])
    with driver.context(driver.CONTEXT_CHROME):
        driver.execute_script("Services.console.reset();")

    # check no HTTPS-First mode logs displayed for HTTPS URL
    panel.open_and_switch_to_new_window("private")
    nav = Navigation(driver)  # The old one caches the closed window's address bar
    nav.search(HTTPS_URL)
    panel.url_contains("https://")
    panel.title_contains("Example Domain")
    assert not console_contains(driver, "HTTPS-First Mode")
