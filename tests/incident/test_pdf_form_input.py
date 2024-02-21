import time
import pytest
import os
import platform
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from pynput.keyboard import Key, Controller


@pytest.fixture()
def test_url():
    return "http://foersom.com/net/HowTo/data/OoPdfFormExample.pdf"


def test_pdf_form_fill(session, test_url):
    # From TestRail: https://testrail.stage.mozaws.net/index.php?/cases/view/1017484
    print(" - TEST: Verify PDF form input")

    this_platform = platform.system()
    # Navigate to the test form
    session.get(test_url)
    WebDriverWait(session, 10).until(
        EC.url_changes("foersom.com/net/HowTo/data/OoPdfFormExample.pdf")
    )

    # Enter full name in the PDF form fields
    # Given name text box element: id=pdfjs_internal_id_5R value="" name="Given Name Text Box"
    given_name_field = WebDriverWait(session, 10).until(
        EC.presence_of_element_located((By.ID, "pdfjs_internal_id_5R"))
    )
    given_name_field.send_keys("Mary")

    # Family name text box element: id=pdfjs_internal_id_7R value="" name="Family Name Text Box"
    family_name_field = session.find_element(By.ID, "pdfjs_internal_id_7R")
    family_name_field.send_keys("Smithsonian")

    # Save the PDF to Downloads
    download_button = session.find_element(By.ID, "download")
    download_button.click()

    # Wait for the system Save dialog
    time.sleep(2)
    keyboard = Controller()

    # On Linux the Save button isn't in focus by default, we have to navigate to it
    if this_platform == "Linux":
        keyboard.press(Key.alt)
        keyboard.press(Key.tab)
        keyboard.release(Key.tab)
        keyboard.release(Key.alt)
        time.sleep(1)
        keyboard.press(Key.alt)
        keyboard.press(Key.tab)
        keyboard.release(Key.tab)
        keyboard.release(Key.alt)
        time.sleep(1)
        keyboard.press(Key.tab)
        keyboard.release(Key.tab)
        time.sleep(1)
        keyboard.press(Key.tab)
        keyboard.release(Key.tab)

    # Press and release the Enter key
    keyboard.press(Key.enter)
    keyboard.release(Key.enter)

    # Wait for the download to complete
    time.sleep(3)

    # Open a new tab after making the first tab blank
    session.get("about:blank")
    print(
        "The title of the tab should be blank !"
        + session.title
        + "! <- Nothing between those"
    )
    session.execute_script("window.open('');")

    # Determine system user and set paths per platform
    saved_pdf_location = ""
    if this_platform == "Windows":
        user = os.environ.get("USERNAME")
        saved_pdf_location = "C:\\Users\\" + user + "\\Downloads\\OoPdfFormExample.pdf"
    elif this_platform == "Darwin":
        user = os.environ.get("USER")
        saved_pdf_location = "/Users/" + user + "/Downloads/OoPdfFormExample.pdf"
    elif this_platform == "Linux":
        user = os.environ.get("USER")
        saved_pdf_location = "/home/" + user + "/Downloads/OoPdfFormExample.pdf"

    saved_pdf_url = "file://" + saved_pdf_location

    # Switch to the new tab and open the saved PDF
    session.switch_to.window(session.window_handles[1])
    session.get(saved_pdf_url)
    WebDriverWait(session, 10).until(EC.title_contains("PDF Form Example"))
    print("Title of the loaded file is: " + session.title)

    # Verify the values in the form fields are correctly filled in
    given_name_saved = WebDriverWait(session, 10).until(
        EC.presence_of_element_located((By.ID, "pdfjs_internal_id_5R"))
    )
    given_value = given_name_saved.get_attribute("value")
    print("The value of the Given name is '" + given_value + "' <- should be 'Mary'")
    assert given_value == "Mary"
    family_name_saved = session.find_element(By.ID, "pdfjs_internal_id_7R")
    family_value = family_name_saved.get_attribute("value")
    print(
        "The value of the Family name is '"
        + family_value
        + "' <- should be 'Smithsonian'"
    )
    assert family_value == "Smithsonian"

    # Close the current tab containing the PDF
    session.close()

    # remove the downloaded PDF from the system
    try:
        os.remove(saved_pdf_location)
        print(saved_pdf_location + " has been deleted.")
    except OSError as error:
        print("There was an error.")
        print(error)
