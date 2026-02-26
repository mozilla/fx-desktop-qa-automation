import pytest
from time import sleep
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from modules.browser_object import TrackerPanel


@pytest.fixture()
def test_case():
    return "192739"


TLS_URL = "https://tls-v1-2.badssl.com:1012/"


def test_tls_v1_2_protocol(driver: Firefox, tracker_panel: TrackerPanel):
    """
    C192739 - TLS v1.2 protocol is handled correctly and returns the proper information
    """
    driver.get(TLS_URL)

    tls_content = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "content"))
    )

    expected_content = "tls-v1-2.\nbadssl.com"
    assert tls_content.text == expected_content, (
        f"Expected '{expected_content}' but found '{tls_content.text}' at {TLS_URL}"
    )
    expected_technical_details = (
        "Connection Encrypted (TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384, 256 bit keys, "
        "TLS 1.2)"
    )

    tracker_panel.open_panel()
    driver.execute_script(
        "arguments[0].click()", tracker_panel.fetch("trustpanel-connect-button")
    )
    tracker_panel.fetch("trustpanel-connect-details-link").click()
    sleep(100)
    tracker_panel.switch_to_new_window()
    technical_details = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "security-technical-shortform"))
    )
