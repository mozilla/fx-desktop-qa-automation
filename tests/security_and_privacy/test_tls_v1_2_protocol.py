from time import sleep

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from modules.browser_object import TrustPanel


@pytest.fixture()
def test_case():
    return "192739"


TLS_URL = "https://tls-v1-2.badssl.com:1012/"
EXPECTED_CONTENT = "tls-v1-2.\nbadssl.com"
EXPECTED_TECHNICAL_DETAILS = (
    "Connection Encrypted "
    "(TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384, 256 bit keys, TLS 1.2)"
)


def test_tls_v1_2_protocol(driver: Firefox, trust_panel: TrustPanel):
    """
    C192739 - TLS v1.2 protocol is handled correctly and returns the proper information
    """
    driver.get(TLS_URL)

    tls_content = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "content"))
    )

    assert tls_content.text == EXPECTED_CONTENT, (
        f"Expected '{EXPECTED_CONTENT}' but found '{tls_content.text}' at {TLS_URL}"
    )

    trust_panel.open_panel()
    sleep(1)
    trust_panel.assert_connection_information(EXPECTED_TECHNICAL_DETAILS)
