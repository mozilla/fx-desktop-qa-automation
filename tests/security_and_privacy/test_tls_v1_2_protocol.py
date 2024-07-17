import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from modules.browser_object_navigation import Navigation

TLS_URL = "https://tls-v1-2.badssl.com:1012/"


@pytest.fixture()
def add_prefs():
    return []


def test_tls_v1_2_protocol(driver: Firefox):
    """
    C192739 - TLS v1.2 protocol is handled correctly and returns the proper information
    """
    nav = Navigation(driver)
    driver.get(TLS_URL)

    tls_content = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "content"))
    )

    expected_content = "tls-v1-2.\nbadssl.com"
    assert (
        tls_content.text == expected_content
    ), f"Expected '{expected_content}' but found '{tls_content.text}' at {TLS_URL}"

    with driver.context(driver.CONTEXT_CHROME):
        nav.get_element("lock-icon").click()
        nav.get_element("connection-secure-button").click()
        nav.get_element("more-information-button").click()

        driver.switch_to.window(driver.window_handles[-1])

        technical_details = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "security-technical-shortform"))
        )

        expected_technical_details = (
            "Connection Encrypted (TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384, 256 bit keys, "
            "TLS 1.2)"
        )
        assert (
            technical_details.get_attribute("value") == expected_technical_details
        ), f"Expected '{expected_technical_details}' but found '{technical_details.get_attribute('value')}'"
