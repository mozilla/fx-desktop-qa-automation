import pytest
from auto_fxui.browser_object import Devtools, Navigation, PanelUi, TrustPanel
from selenium.webdriver import Firefox

SCHEMELESS_TEST_URL = "help.websiteos.com/websiteos/example_of_a_simple_html_page.htm"
HTTP_TEST_URL = "http://www.testingmcafeesites.com/"

SCHEMELESS_UPGRADE_MESSAGE = (
    "HTTPS-First Mode: Upgrading insecure request “http://help.websiteos.com/websiteos/example_of_a_simple_html_page.htm” "
    "to use “https”."
)
SCHEMELESS_EXCEPTION_MESSAGE = (
    "HTTPS-First Mode: Upgrading insecure request “https://help.websiteos.com/websiteos/example_of_a_simple_html_page.htm” "
    "failed. Downgrading to “http” again."
)
HTTP_UPGRADE_MESSAGE = "HTTPS-First Mode: Upgrading insecure speculative TCP connection “http://www.testingmcafeesites.com/” to use “https”."
HTTP_EXCEPTION_MESSAGE = "HTTPS-First Mode: Adding exception to temporarily prevent further attempts to automatically load “http://www.testingmcafeesites.com” securely."


@pytest.fixture()
def test_case():
    return "1364748"


@pytest.fixture()
def add_to_prefs_list():
    return [("dom.security.https_first_pbm", True)]


def test_http_fallback_for_unsupported_https(driver: Firefox):
    """
    C1364748 - Check that the connection falls back to HTTP when HTTPS is not supported
    """

    # Instantiate objects
    panel = PanelUi(driver)
    nav = Navigation(driver)
    devtools = Devtools(driver)
    trust_panel = TrustPanel(driver)

    # Check schemeless test URL upgrade fails and console contains exception message
    panel.open_and_switch_to_new_window("private")
    nav.search(SCHEMELESS_TEST_URL)
    panel.url_contains("http://")
    trust_panel.element_visible("shield-icon-insecure")
    devtools.expect_console_contains(SCHEMELESS_UPGRADE_MESSAGE)
    devtools.expect_console_contains(SCHEMELESS_EXCEPTION_MESSAGE)

    # Check HTTP test URL upgrade fails and console contains exception message
    panel.open_and_switch_to_new_window("tab")
    nav.search(HTTP_TEST_URL)
    panel.url_contains("http://")
    trust_panel.element_visible("shield-icon-insecure")
    devtools.expect_console_contains(HTTP_UPGRADE_MESSAGE)
    devtools.expect_console_contains(HTTP_EXCEPTION_MESSAGE)
