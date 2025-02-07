import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.support.wait import WebDriverWait


@pytest.fixture()
def test_case():
    return "1362731"


HTTP_URL = "http://example.com"


@pytest.fixture()
def add_prefs():
    return [
        ("browser.privatebrowsing.autostart", True),
        ("dom.security.https_first_pbm", True),
    ]


@pytest.mark.skip("136.0b3 security changes")
def test_https_first_mode_in_private_browsing(driver: Firefox):
    """
    C1362731 Check that https First Mode is properly enabled and working in Private Browsing
    """

    # Navigate to the HTTP URL
    driver.get(HTTP_URL)

    # Wait for the URL to be redirected to HTTPS
    assert WebDriverWait(driver, 10).until(
        lambda d: d.current_url.startswith("https://"),
        message=f"Final URL should use HTTPS, but was: {driver.current_url}",
    )
