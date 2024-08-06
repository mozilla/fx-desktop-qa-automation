import os
import time
import platform
import pytest
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from pynput.keyboard import Controller, Key

from modules.browser_object_navigation import Navigation
from modules.page_object import GenericPdf

@pytest.fixture()
def add_prefs():
    return []

def test_pdf_download(driver: Firefox, fillable_pdf_url: str):
    """
    C3932: PDF files can be successfully downloaded via pdf.js
    """
    GenericPdf(driver, pdf_url=fillable_pdf_url).open()
    nav = Navigation(driver)
    keyboard = Controller()

    # Click the download button
    download_button = driver.find_element(By.ID, "download")
    download_button.click()

    # Allow time for the download dialog m to appear and pressing enter to download
    time.sleep(2)
    keyboard.press(Key.enter)
    keyboard.release(Key.enter)

    # Allow time for the download to complete
    time.sleep(2)

    # Determine the platform and set the expected download path
    this_platform = platform.system()
    saved_pdf_location = ""
    file_name = "i-9.pdf"

    if this_platform == "Windows":
        user = os.environ.get("USERNAME")
        saved_pdf_location = f"C:\\Users\\{user}\\Downloads\\{file_name}"
    elif this_platform == "Darwin":  # MacOS
        user = os.environ.get("USER")
        saved_pdf_location = f"/Users/{user}/Downloads/{file_name}"
    elif this_platform == "Linux":
        user = os.environ.get("USER")
        saved_pdf_location = f"/home/{user}/Downloads/{file_name}"

    # Verify if the file exists
    assert os.path.exists(saved_pdf_location), f"The file was not downloaded to {saved_pdf_location}."

    print(f"Test passed: The file {file_name} has been downloaded and is present at {saved_pdf_location}.")