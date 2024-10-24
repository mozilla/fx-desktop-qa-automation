from time import sleep
import pytest
from selenium.webdriver import Firefox
from selenium.common.exceptions import TimeoutException

from modules.browser_object import Navigation
from modules.page_object import AboutPrefs


@pytest.fixture()
def test_case():
    return "2300294"

@pytest.fixture()
def set_prefs():
    return [
        ("browser.safebrowsing.blockedURIs.enabled", False),
        ("browser.safebrowsing.downloads.enabled", False),
        ("browser.safebrowsing.malware.enabled", False),
        ("browser.safebrowsing.phishing.enabled", False)
    ]
    # ("browser.contentblocking.features.standard", "tp,tpPrivate,cm,fp")

HTTP_SITE = "http://www.http2demo.io/"
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
    except TimeoutException:
        pass

    # Unblocking - non-private only

    # Private browsing - blocked
