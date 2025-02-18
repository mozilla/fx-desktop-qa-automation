import re

import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from modules.page_object import GenericPage


@pytest.fixture()
def test_case():
    return "1756722"


@pytest.fixture()
def delete_files_regex_string():
    return r"\bdownload\b"


MIXED_CONTENT_DOWNLOAD_URL = "https://b-mcb-download.glitch.me/"


def test_mixed_content_download_via_https(driver: Firefox, delete_files):
    """
    C1756722: Verify that the user can download mixed content via HTTPS
    """

    web_page = GenericPage(driver, url=MIXED_CONTENT_DOWNLOAD_URL)

    # Wait up to 30 seconds for test website to wake up and load the content
    web_page.open()
    with driver.context(driver.CONTEXT_CHROME):
        WebDriverWait(driver, 30).until(EC.title_contains("Hello!"))

    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, "//button[@onclick='runtestSec()']"))
    ).click()

    with driver.context(driver.CONTEXT_CHROME):
        download_name = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "downloadTarget"))
        )

        download_status = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "downloadProgress"))
        )

        # Verify that the desired download target element is present directly, no extra steps needed.
        download_value = download_name.get_attribute("value")
        assert re.match(r"download(\(\d+\))?$", download_value), (
            f"The download name is incorrect: {download_value}"
        )

        # Verify that the download progress has reached 100%, which indicates that the download is complete.
        download_status_value = download_status.get_attribute("value")
        assert download_status_value == "100", (
            f"The download status is not '100': {download_status_value}"
        )
