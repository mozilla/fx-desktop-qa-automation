import pytest
from selenium.common import TimeoutException
from selenium.webdriver import Firefox
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

HTTP_URL = "http://example.com"


@pytest.fixture()
def add_prefs():
    return [
        ("browser.privatebrowsing.autostart", True),
        ("dom.security.https_first_pbm", True),
    ]


def test_https_first_mode_in_private_browsing(driver: Firefox):
    """
    C1362731 Check that https First Mode is properly enabled and working in Private Browsing
    """

    # Navigate to the HTTP URL
    driver.get(HTTP_URL)

    try:
        # Wait for the URL to be redirected to HTTPS
        WebDriverWait(driver, 10).until(EC.url_contains("https://example.com/"))
    except TimeoutException:
        pytest.fail(
            f"Timed out waiting for URL to switch to HTTPS: {driver.current_url}"
        )

        # Assertion to ensure URL starts with HTTPS
    assert driver.current_url.startswith(
        "https://"
    ), f"Final URL should be 'https://example.com/', but was: {driver.current_url}"
